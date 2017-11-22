from typing import *
import multiprocessing as mp
from worker.work_result import WorkResult
from hapi import *
import utils.fetch_handler
from utils.log import *
from utils.config import Config
from utils.hapi_metadata import HapiMetaData
from utils.hapiest_util import echo

class WorkFunctions:
    @staticmethod
    def start_hapi(**kwargs) -> bool:
        print('Initializing hapi db...')
        try:
            db_begin(Config.data_folder)
            print('Done initializing hapi db...')
        except Exception as e:
            print('Error initializing hapi db...')
            return False
        return True

    graph_type_map = {
        "Voigt": absorptionCoefficient_Voigt,
        "Lorentz": absorptionCoefficient_Lorentz,
        "Gauss": absorptionCoefficient_Gauss,
        "SD Voigt": absorptionCoefficient_SDVoigt,
        "Galatry": absorptionCoefficient_Doppler,
        "HT": absorptionCoefficient_HT
    }

    @staticmethod
    def try_graph_absorption_coefficient(
            graph_fn: Callable, Components: List[Tuple['MoleculeId', 'IsotopologueId']], SourceTables: List[str],
            Environment: Dict[str, Any], GammaL: str, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
            WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
            **kwargs) -> Union[Dict[str, Any], Exception]:
        try:
            x, y = WorkFunctions.graph_type_map[graph_fn](
                Components=Components,
                SourceTables=SourceTables,
                Environment=Environment,
                GammaL=GammaL,
                HITRAN_units=False,
                WavenumberRange=WavenumberRange,
                WavenumberStep=WavenumberStep,
                WavenumberWing=WavenumberWing,
                WavenumberWingHW=WavenumberWingHW)
            return {'x': x, 'y': y, 'title': title, 'titlex': titlex, 'titley': titley}
        except Exception as e:
            return e

    @staticmethod
    def try_fetch(data_name: str, iso_id_list: List['GlobalIsotopologueId'], numin: float, numax: float,
                  parameter_groups: List[str] = (), parameters: List[str] = (), **kwargs) -> Union[bool, 'FetchError']:
        if len(iso_id_list) == 0:
            return utils.fetch_handler.FetchError(utils.fetch_handler.FetchErrorKind.BadIsoList,
                              'Fetch Failure: Iso list cannot be empty.')
        try:
            fetch_by_ids(data_name, iso_id_list, numin, numax, parameter_groups, parameters)
            hmd = HapiMetaData.write(data_name, iso_id_list)
        except Exception as e:
            as_str = str(e)
            # Determine whether the issue is an internet issue or something else
            if 'connect' in as_str:
                return utils.fetch_handler.FetchError(
                    utils.fetch_handler.FetchErrorKind.BadConnection,
                    'Bad connection: Failed to connect to send request. Check your connection.')
            else:
                return utils.fetch_handler.FetchError(
                    utils.fetch_handler.FetchErrorKind.FailedToRetreiveData,
                    'Fetch failure: Failed to fetch data (connected successfully, received HTTP error as response)')
        return True

    @staticmethod
    def table_get_lines_page(table_name: str, page_len: int, page_number: int) -> Union[bool, Dict[str, Any]]:
        start_index = page_len * page_number
        end_index = start_index + page_len
        result: Dict[str, List[Union[int, float]]] = {}
        table = LOCAL_TABLE_CACHE[table_name]['data']
        last_page = False
        for (param, param_data) in table.items():
            if len(param_data) <= end_index + page_len:
                last_page = True
            break
        for (param, param_data) in table.items():
            if len(param_data) < end_index:
                end_index = len(param_data)
                last_page = True
            result[param] = param_data[start_index:end_index]

        return echo(table_name=table_name, parameters=result, page_number=page_number, page_len=page_len,
                    last_page=last_page)

    @staticmethod
    def table_commit_lines_page(table_name: str, start_index: int, data: Dict[str, List[Union[int, float]]]) -> bool:
        table = LOCAL_TABLE_CACHE[table_name]['data']
        for (parameter, param_data) in data.items():
            param = table[parameter]
            for i in range(start_index, start_index + len(param_data)):
                param[i] = param_data[i - start_index]

        return True

    @staticmethod
    def table_write_to_disk(**kwargs):
        try:
            db_commit()
        except Exception as e:
            return e
        return True

class WorkRequest:
    def __init__(self, job_id: int, work_type: Any, work_args: Dict[str, Any]):
        self.job_id = job_id
        self.work_type = work_type
        self.work_args = work_args

    WorkType = int

    START_HAPI: WorkType = 0
    END_WORK_PROCESS: WorkType = 1
    FETCH: WorkType = 2
    ABSORPTION_COEFFICIENT: WorkType = 3
    TABLE_META_DATA: WorkType = 4
    TABLE_GET_LINES_PAGE: WorkType = 5
    TABLE_COMMIT_LINES_PAGE: WorkType = 6
    TABLE_WRITE_TO_DISK: WorkType = 7

    WORKQ: mp.Queue = mp.Queue()
    RESULTQ: mp.Queue = mp.Queue()

    WORKER: 'Work' = None

    WORK_FUNCTIONS: Dict[int, Callable] = {
        START_HAPI: WorkFunctions.start_hapi,
        FETCH: WorkFunctions.try_fetch,
        ABSORPTION_COEFFICIENT: WorkFunctions.try_graph_absorption_coefficient,
        TABLE_GET_LINES_PAGE: WorkFunctions.table_get_lines_page,
        TABLE_COMMIT_LINES_PAGE: WorkFunctions.table_commit_lines_page,
        TABLE_WRITE_TO_DISK: WorkFunctions.table_write_to_disk
    }

    def do_work(self) -> Any:
        if self.work_type in WorkRequest.WORK_FUNCTIONS:
            fn = WorkRequest.WORK_FUNCTIONS[self.work_type]
            exec_res = fn(**self.work_args)
            return WorkResult(self.job_id, exec_res)
        else:
            return WorkResult(self.job_id, False)

    @staticmethod
    def start_work_process():
        WorkRequest.WORKER = Work()


class Work:
    @staticmethod
    def WORK_FUNCTION(workq: mp.Queue, resultq: mp.Queue) -> int:
        while True:
            work_request = workq.get()
            if work_request.work_type == WorkRequest.END_WORK_PROCESS:
                return 0
            else:
                result = work_request.do_work()
                resultq.put(result)

    def __init__(self):
        self.process: mp.Process = mp.Process(target=Work.WORK_FUNCTION, args=(WorkRequest.WORKQ, WorkRequest.RESULTQ))
        self.process.start()

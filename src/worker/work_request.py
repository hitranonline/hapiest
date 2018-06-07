from typing import *
import multiprocessing as mp
from worker.work_result import WorkResult
from hapi import *
from utils.fetch_error import FetchErrorKind, FetchError
from utils.log import *
from utils.config import Config
from utils.hapi_metadata import HapiMetaData
from utils.hapiest_util import echo
import sys
import traceback

class WorkFunctions:
    @staticmethod
    def start_hapi(**kwargs) -> bool:
        """
        *Initilizes hapi, calls db begin, error handling.*
        """
        print('Initializing hapi db...')
        try:
            db_begin(Config.data_folder)
            del LOCAL_TABLE_CACHE['sampletab']
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

    instrumental_fn_map = {
        "rectangular": SLIT_RECTANGULAR,
        "triangular": SLIT_TRIANGULAR,
        "gaussian": SLIT_GAUSSIAN,
        "diffraction": SLIT_DIFFRACTION,
        "michelson": SLIT_MICHELSON,
        "dispersion": SLIT_DISPERSION
    }

    @staticmethod
    def convolve_spectrum(x, y, instrumental_fn: str, Resolution: float, AF_wing: float):
        """
        *Calls proper method if user selected instrumental_fn to be used, otherwise uses original x and y coordinate arrays, calls convolve spectrum method form hapi.*
        """
        instrumental_fn = instrumental_fn.lower()
        if instrumental_fn not in WorkFunctions.instrumental_fn_map:
            return x, y
        else:
            newx, newy, i, j, slit = convolveSpectrum(x, y, Resolution=Resolution, AF_wing=AF_wing,
                                                      SlitFunction=WorkFunctions.instrumental_fn_map[instrumental_fn])
            return newx, newy

    @staticmethod
    def graph_absorption_coefficient(
            graph_fn: str, Components: List[Tuple[int, int]], SourceTables: List[str],
            Environment: Dict[str, Any], Diluent: dict, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
            WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
            **kwargs) -> Union[Dict[str, Any], Exception]:
        """
        *Generates coordinates for absorption coeffecient graph.*
        """
        kwargs = { 'WavenumberRange': WavenumberRange, 'Environment': Environment, 'graph_fn': graph_fn,
                   'Diluent': Diluent }
        # absorptionCoefficient_Doppler functions do not use Diluent
        if WorkFunctions.graph_type_map[graph_fn] == WorkFunctions.graph_type_map["Galatry"]:
            x, y = WorkFunctions.graph_type_map[graph_fn](
                Components=Components,
                SourceTables=SourceTables,
                Environment=Environment,
                HITRAN_units=False,
                WavenumberRange=WavenumberRange,
                WavenumberStep=WavenumberStep,
                WavenumberWing=WavenumberWing,
                WavenumberWingHW=WavenumberWingHW) 
        else:
            x, y = WorkFunctions.graph_type_map[graph_fn](
                Components=Components,
                SourceTables=SourceTables,
                Environment=Environment,
                Diluent=Diluent,
                HITRAN_units=False,
                WavenumberRange=WavenumberRange,
                WavenumberStep=WavenumberStep,
                WavenumberWing=WavenumberWing,
                WavenumberWingHW=WavenumberWingHW)
        return { 'x': x, 'y': y, 'title': title, 'name': SourceTables[0], 'titlex': titlex, 'titley': titley,
                 'args': kwargs }

    @staticmethod
    def graph_absorption_spectrum(
            graph_fn: str, Components: List[Tuple[int, int]], SourceTables: List[str],
            Environment: Dict[str, Any], Diluent: dict, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
            WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
            Format='%e %e', path_length=100.0, File=None, instrumental_fn: str = "",
            Resolution: float = 0.01, AF_wing: float = 100.0, **kwargs) -> Union[Dict[str, Any], Exception]:
        """
        *Generates coordinates for absorption spectrum graph.*
        """
        kwargs = { 'WavenumberRange': WavenumberRange, 'Environment': Environment, 'graph_fn': graph_fn,
                   'Diluent': Diluent }
        wn, ac = WorkFunctions.graph_type_map[graph_fn](
            Components=Components,
            SourceTables=SourceTables,
            Environment=Environment,
            Diluent=Diluent,
            HITRAN_units=False,
            WavenumberRange=WavenumberRange,
            WavenumberStep=WavenumberStep,
            WavenumberWing=WavenumberWing,
            WavenumberWingHW=WavenumberWingHW)
        Environment = { 'l': path_length }
        x, y = absorptionSpectrum(wn, ac, Environment=Environment, File=File, Format=Format)
        rx, ry = WorkFunctions.convolve_spectrum(x, y, instrumental_fn, Resolution=Resolution, AF_wing=AF_wing)
        return { 'x': rx, 'y': ry, 'title': title, 'name': SourceTables[0], 'titlex': titlex,
                 'titley': titley, 'args': kwargs }

    @staticmethod
    def graph_radiance_spectrum(
            graph_fn: str, Components: List[Tuple[int, int]], SourceTables: List[str],
            Environment: Dict[str, Any], Diluent: dict, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
            WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
            Format='%e %e', path_length=100.0, temp=296.0, File=None, instrumental_fn: str = "",
            Resolution: float = 0.01, AF_wing: float = 100.0, **kwargs) -> Union[Dict[str, Any], Exception]:
        """
        *Generates coordinates for radiance spectrum graph.*
        """
        kwargs = { 'WavenumberRange': WavenumberRange, 'Environment': Environment, 'graph_fn': graph_fn,
                   'Diluent': Diluent }
        wn, ac = WorkFunctions.graph_type_map[graph_fn](
            Components=Components,
            SourceTables=SourceTables,
            Environment=Environment,
            Diluent=Diluent,
            HITRAN_units=False,
            WavenumberRange=WavenumberRange,
            WavenumberStep=WavenumberStep,
            WavenumberWing=WavenumberWing,
            WavenumberWingHW=WavenumberWingHW)
        Environment['l'] = path_length
        x, y = radianceSpectrum(wn, ac, Environment=Environment, File=File, Format=Format)
        rx, ry = WorkFunctions.convolve_spectrum(x, y, instrumental_fn, Resolution=Resolution, AF_wing=AF_wing)
        return { 'x': rx, 'y': ry, 'title': title, 'name': SourceTables[0], 'titlex': titlex,
                 'titley': titley, 'args': kwargs }

    @staticmethod
    def graph_transmittance_spectrum(
            graph_fn: str, Components: List[Tuple[int, int]], SourceTables: List[str],
            Environment: Dict[str, Any], Diluent: dict, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
            WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
            Format='%e %e', path_length=100.0, File=None, instrumental_fn: str = "",
            Resolution: float = 0.01, AF_wing: float = 100.0, **kwargs) -> Union[Dict[str, Any], Exception]:
        """
        *Generates coordinates for transmittance spectrum graph.*
        """
        kwargs = { 'WavenumberRange': WavenumberRange, 'Environment': Environment, 'graph_fn': graph_fn,
                   'Diluent': Diluent }
        wn, ac = WorkFunctions.graph_type_map[graph_fn](
            Components=Components,
            SourceTables=SourceTables,
            Environment=Environment,
            Diluent=Diluent,
            HITRAN_units=False,
            WavenumberRange=WavenumberRange,
            WavenumberStep=WavenumberStep,
            WavenumberWing=WavenumberWing,
            WavenumberWingHW=WavenumberWingHW)
        Environment = {'l': path_length}
        x, y = transmittanceSpectrum(wn, ac, Environment=Environment, File=File, Format=Format)
        rx, ry = WorkFunctions.convolve_spectrum(x, y, instrumental_fn, Resolution=Resolution, AF_wing=AF_wing)
        return { 'x': rx, 'y': ry, 'title': title, 'name': SourceTables[0], 'titlex': titlex,
                 'titley': titley, 'args': kwargs }


    @staticmethod
    def fetch(data_name: str, iso_id_list: List[int], numin: float, numax: float,
                  parameter_groups: List[str] = (), parameters: List[str] = (), **kwargs) -> Union[
        Dict[str, List[str]], 'FetchError']:
        """
        *Method handles verification of user input for fetch function.*
        """
        if len(iso_id_list) == 0:
            return FetchError(FetchErrorKind.BadIsoList,
                              'Fetch Failure: Iso list cannot be empty.')
        try:
            fetch_by_ids(data_name, iso_id_list, numin, numax, parameter_groups, parameters)
            hmd = HapiMetaData(data_name, iso_id_list, numin, numax)
        except Exception as e:
            debug('Fetch error: ', e)
            as_str = str(e)
            # Determine whether the issue is an internet issue or something else
            if 'connect' in as_str:
                return FetchError(
                    FetchErrorKind.BadConnection,
                    'Bad connection: Failed to connect to send request. Check your connection.')
            else:
                return FetchError(
                    FetchErrorKind.FailedToRetreiveData,
                    'Fetch failure: Failed to fetch data (connected successfully, received HTTP error as response)')
        return { 'all_tables': list(tableList()) }

    @staticmethod
    def table_get_lines_page(table_name: str, page_len: int, page_number: int) -> Union[bool, Dict[str, Any]]:
        """
        *Reads the page_number'th page from table table_name, with page length page_len.*
        """
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
        """
        *Caches data from edit tab to local machine.*
        """
        table = LOCAL_TABLE_CACHE[table_name]['data']
        for (parameter, param_data) in data.items():
            param = table[parameter]
            for i in range(start_index, start_index + len(param_data)):
                param[i] = param_data[i - start_index]

        return True

    @staticmethod
    def table_write_to_disk(source_table: str, output_table: str = None, **kwargs):
        """
        *Attempts to save cached data to local machine.*
        """
        if source_table == output_table:
            cache2storage(TableName=source_table)
            hmd = HapiMetaData(source_table)
            hmd.initialize_from_hapi_table(source_table)
            hmd.save()
        else:
            select(DestinationTableName=output_table, TableName=source_table, Conditions=None, ParameterNames=None)
            cache2storage(TableName=output_table)
            hmd = HapiMetaData(output_table)
        return True

    @staticmethod
    def table_meta_data(table_name: str):
        """
        *Initilizes meta data file.*
        """
        table = LOCAL_TABLE_CACHE[table_name]['data']
        header = LOCAL_TABLE_CACHE[table_name]['header']
        parameters = list(table.keys())
        length = header['number_of_rows']
        return echo(length=length, header=header, parameters=parameters)

    @staticmethod
    def table_names(**kwargs):
        """
        *Returns all table names in local cache.*
        """
        table_names = []
        for (table_name, table) in LOCAL_TABLE_CACHE.items():
            table_names.append(table_name)

        return echo(table_names=table_names)

    # def select(TableName,DestinationTableName=QUERY_BUFFER,ParameterNames=None,Conditions=None,Output=True,File=None):
    @staticmethod
    def select(TableName: str, DestinationTableName: str = QUERY_BUFFER, ParameterNames: List[str] = None,
                   Conditions: List[Any] = None, Output: bool = False, File=None, **kwargs):
        """
        *Attempts to call the select() method from hapi.*
        """
        select(TableName=TableName, DestinationTableName=DestinationTableName, ParameterNames=ParameterNames,
              Conditions=Conditions, Output=Output, File=File)
        hmd = HapiMetaData(DestinationTableName)
        WorkFunctions.table_write_to_disk(source_table=TableName, output_table=DestinationTableName)

        return echo(new_table_name=DestinationTableName, all_tables=list(tableList()))

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
    TABLE_NAMES: WorkType = 8
    SELECT: WorkType = 9
    TRANSMITTANCE_SPECTRUM: WorkType = 10
    RADIANCE_SPECTRUM: WorkType = 11
    ABSORPTION_SPECTRUM: WorkType = 12

    WORKQ: mp.Queue = mp.Queue()
    RESULTQ: mp.Queue = mp.Queue()

    WORKER: 'Work' = None

    WORK_FUNCTIONS: Dict[WorkType, Callable] = {}

    def do_work(self) -> Any:
        """
        *Executes the appropriate function, based on the specified work_type in the work request.*
        """
        if self.work_type in WorkRequest.WORK_FUNCTIONS:
            fn = WorkRequest.WORK_FUNCTIONS[self.work_type]
            exec_res = fn(**self.work_args)
            return WorkResult(self.job_id, exec_res)

        return WorkResult(self.job_id, False)

    @staticmethod
    def start_work_process():
        WorkRequest.WORKER = Work()


class Work:
    @staticmethod
    def WORK_FUNCTION(workq: mp.Queue, resultq: mp.Queue) -> int:
        """
        *Handles the calling of most hapi functions.*
        """
        WorkRequest.WORK_FUNCTIONS = {
            WorkRequest.START_HAPI: WorkFunctions.start_hapi,
            WorkRequest.FETCH: WorkFunctions.fetch,
            WorkRequest.ABSORPTION_COEFFICIENT: WorkFunctions.graph_absorption_coefficient,
            WorkRequest.TABLE_GET_LINES_PAGE: WorkFunctions.table_get_lines_page,
            WorkRequest.TABLE_COMMIT_LINES_PAGE: WorkFunctions.table_commit_lines_page,
            WorkRequest.TABLE_WRITE_TO_DISK: WorkFunctions.table_write_to_disk,
            WorkRequest.TABLE_NAMES: WorkFunctions.table_names,
            WorkRequest.TABLE_META_DATA: WorkFunctions.table_meta_data,
            WorkRequest.SELECT: WorkFunctions.select,
            WorkRequest.ABSORPTION_SPECTRUM: WorkFunctions.graph_absorption_spectrum,
            WorkRequest.TRANSMITTANCE_SPECTRUM: WorkFunctions.graph_transmittance_spectrum,
            WorkRequest.RADIANCE_SPECTRUM: WorkFunctions.graph_radiance_spectrum
        }

        WorkFunctions.start_hapi(**{})
        def print_tb(tb, exc_value):
            print('\n'.join([''] + traceback.format_tb(tb) + [str(exc_value)]).replace('\n', '\n    |   ') + '\n')


        while True:
            work_request = workq.get()
            if work_request.work_type == WorkRequest.END_WORK_PROCESS:
                return 0
            else:
                result = None
                try:
                    result = work_request.do_work()
                except Exception as e:
                    exc_ty, exc_val, exc_tb = sys.exc_info()
                    print_tb(exc_tb, exc_val)
                    debug('Error executing work request: ', e, type(e), result)
                    result = WorkResult(e, False)
                finally:
                    resultq.put(result)

    def __init__(self):
        self.process: mp.Process = mp.Process(target=Work.WORK_FUNCTION, args=(WorkRequest.WORKQ, WorkRequest.RESULTQ))
        self.process.start()

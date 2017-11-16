from utils.hapiest_util import *
from PyQt5 import QtWidgets, QtCore
import sys
import time
from utils.hapiest_util import *
from utils.isotopologue import *
from multiprocessing import Queue
import multiprocessing as mp
from utils.log import *
from utils.fetch_handler import *
from utils.hapi_metadata import *


class WorkWriter:
    def __init__(self, outq: Queue):
        self.outq = outq

    def write(self, x: Dict[str, Any]) -> None:
        self.outq.put((0, x))


def WORK_FUNCTION(workq, resultq) -> int:
    while True:
        sys.stdout.flush()
        (job_id, workargs) = workq.get()
        type = workargs['type']
        if type == Work.END_WORK_PROCESS:
            return 0
        resultq.put((job_id, Work.do_work(type, workargs)))


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


def try_graph_absorption_coefficient(
        graph_fn: Callable, Components: List[Tuple[MoleculeId, IsotopologueId]], SourceTables: List[str],
        Environment: Dict[str, Any], GammaL: str, HITRAN_units: bool, WavenumberRange: Tuple[float, float],
        WavenumberStep: float, WavenumberWing: float, WavenumberWingHW: float, title: str, titlex: str, titley: str,
        **kwargs) -> Dict[str, Any]:
    try:
        x, y = graph_type_map[graph_fn](
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


def try_fetch(data_name: str, iso_id_list: List[GlobalIsotopologueId], numin: float, numax: float,
              parameter_groups: List[str] = (), parameters: List[str] = (), **kwargs) -> Union[
    bool, 'FetchError']:
    if len(iso_id_list) == 0:
        return FetchError(FetchErrorKind.BadIsoList,
                          'Fetch Failure: Iso list cannot be empty.')
    try:
        fetch_by_ids(data_name, iso_id_list, numin, numax, parameter_groups, parameters)
        hmd = HapiMetaData.write(data_name, iso_id_list)
    except Exception as e:
        as_str = str(e)
        print(as_str, file=sys.stderr)
        # Determine whether the issue is an internet issue or something else
        if 'connect' in as_str:
            return FetchError(
                FetchErrorKind.BadConnection,
                'Bad connection: Failed to connect to send request. Check your connection.')
        else:
            return FetchError(
                FetchErrorKind.FailedToRetreiveData,
                'Fetch failure: Failed to fetch data (connected successfully, received HTTP error as response)')
    return True


# A (mostly static) class that contains utilities for
class Work:
    START_HAPI: int = 0
    END_WORK_PROCESS: int = 1
    FETCH: int = 2
    ABSORPTION_COEFFICIENT: int = 3

    WORKQ: Queue = mp.Queue()
    RESULTQ: Queue = mp.Queue()

    WORKER: 'Work' = None

    WORK_FUNCTIONS: Dict[int, Callable] = {
        START_HAPI: start_hapi,
        FETCH: try_fetch,
        ABSORPTION_COEFFICIENT: try_graph_absorption_coefficient
    }

    @staticmethod
    def do_work(type: int, workargs: Dict[str, Any]) -> Any:
        if type in Work.WORK_FUNCTIONS:
            fn = Work.WORK_FUNCTIONS[type]
            return fn(**workargs)
        else:
            return None

    @staticmethod
    def start_work_process():
        Work.WORKER = Work()

    def __init__(self):
        self.process: mp.Process = mp.Process(target=WORK_FUNCTION, args=(Work.WORKQ, Work.RESULTQ))
        self.process.start()


class HapiWorker(QtCore.QThread):
    job_id: int = 0

    step_signal = QtCore.pyqtSignal(object)
    done_signal = QtCore.pyqtSignal(object)

    job_results: List[Tuple[int, Any]] = []

    # Used to create a map from named arguments
    @staticmethod
    def echo(**kwargs) -> Dict[str, Any]:
        return kwargs

    def __init__(self, work: Dict[str, Any], callback: Callable = None):
        super(HapiWorker, self).__init__()
        self.callback = callback
        self.work: Dict[str, Any] = work
        self.work['job_id'] = HapiWorker.job_id
        HapiWorker.job_id += 1

        self.started.connect(self.__run)

        if work['type'] == Work.END_WORK_PROCESS:
            Work.WORKQ.put((self.work['job_id'], self.work))
            return
        self.step_signal.connect(lambda x: QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents))

        if callback:
            self.done_signal.connect(self.callback)

    def __run(self):
        job_id = self.work['job_id']
        Work.WORKQ.put((job_id, self.work))
        while True:
            time.sleep(0.01)
            try:
                (job_id, item) = Work.RESULTQ.get_nowait()
                if job_id == self.work['job_id']:
                    self.done_signal.emit(item)
                    return
                HapiWorker.job_results.append((job_id, item))
            except Exception as e:
                self.step_signal.emit({})
            finally:
                for item in HapiWorker.job_results:
                    (job_id, result) = item
                    if job_id == self.work['job_id']:
                        HapiWorker.job_results.remove(item)
                        self.done_signal.emit(result)
                        return

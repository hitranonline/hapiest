from PyQt5 import QtGui, QtWidgets, uic, QtCore
from hapiest_util import *
import hapiest_util
import multiprocessing as mp
import data_handle
import pickle
from absorption_coefficient_window import *


class WorkWriter():
    def __init__(self, outq):
        self.outq = outq

    def write(self, x):
        self.outq.put((0, x))


def WORK_FUNCTION(workq, resultq):
    while True:
        (job_id, workargs) = workq.get()
        type = workargs['type']
        if type == Work.END_WORK_PROCESS:
            return 0
        resultq.put((job_id, Work.do_work(type, workargs)))


def start_hapi(**kwargs):
    print('Initializing hapi db...')
    db_begin(Config.data_folder)
    print('Done initializing hapi db...')
    return True


def try_graph_absorption_coefficient(graph_fn, Components, SourceTables, Environment, GammaL, HITRAN_units,
                                     WavenumberRange,
                                     WavenumberStep, WavenumberWing, WavenumberWingHW, title, titlex, titley, **kwargs):
    try:
        x, y = AbsorptionCoefficientWindow.graph_type_map[graph_fn](
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


def try_fetch(data_name, iso_id_list, numin, numax, parameter_groups=[], parameters=[], **kwargs):
    if len(iso_id_list) == 0:
        return data_handle.FetchError(data_handle.FetchErrorKind.BadIsoList,
                                      'Fetch Failure: Iso list cannot be empty.')
    try:
        fetch_by_ids(data_name, iso_id_list, numin, numax, parameter_groups, parameters)
        hmd = HMD.write(data_name, iso_id_list)
    except Exception as e:
        as_str = str(e)
        print(as_str, file=sys.stderr)
        # Determine whether the issue is an internet issue or something else
        if 'connect' in as_str:
            return data_handle.FetchError(
                data_handle.FetchErrorKind.BadConnection,
                'Bad connection: Failed to connect to send request. Check your connection.')
        else:
            return data_handle.FetchError(
                data_handle.FetchErrorKind.FailedToRetreiveData,
                'Fetch failure: Failed to fetch data (connected successfully, received HTTP error as response)')
    return True


# A (mostly static) class that contains utilities for
class Work():
    START_HAPI = 0
    END_WORK_PROCESS = 1
    FETCH = 2
    ABSORPTION_COEFFICIENT = 3

    WORKQ = mp.Queue()
    RESULTQ = mp.Queue()

    WORKER = None

    WORK_FUNCTIONS = {
        START_HAPI: start_hapi,
        FETCH: try_fetch,
        ABSORPTION_COEFFICIENT: try_graph_absorption_coefficient
    }

    @staticmethod
    def do_work(type, workargs):
        if type in Work.WORK_FUNCTIONS:
            fn = Work.WORK_FUNCTIONS[type]
            return fn(**workargs)
        else:
            return None

    @staticmethod
    def start_work_process():
        Work.WORKER = Work()

    def __init__(self):
        self.process = mp.Process(target=WORK_FUNCTION, args=(Work.WORKQ, Work.RESULTQ))
        self.process.start()


class HapiWorker(QtCore.QThread):
    job_id = 0

    step_signal = QtCore.pyqtSignal(object)
    done_signal = QtCore.pyqtSignal(object)

    job_results = []

    # Used to create a map from named arguments
    @staticmethod
    def echo(**kwargs):
        return kwargs

    def __init__(self, work, callback=None):
        super(HapiWorker, self).__init__()
        self.callback = callback
        self.work = work
        self.work['job_id'] = HapiWorker.job_id
        HapiWorker.job_id += 1


        self.started.connect(self.__run)

        def t():
            try:
                QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents)
            except Exception as e:
                hapiest_util.debug(e)

        def call(x):
            try:
                self.callback(x)
            except Exception as e:
                hapiest_util.debug(e)

        self.step_signal.connect(lambda x: t())

        if callback:
            self.done_signal.connect(call)

        self.kwargs = []

    def __run(self):
        job_id = self.work['job_id']
        Work.WORKQ.put((job_id, self.work))
        while True:
            sleep(0.1)
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

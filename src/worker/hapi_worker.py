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
from worker.work_result import WorkResult
from worker.work_request import *

class HapiWorker(QtCore.QThread):
    job_id: int = 0

    step_signal = QtCore.pyqtSignal(object)
    done_signal = QtCore.pyqtSignal(object)

    job_results: List[WorkResult] = []

    # Used to create a map from named arguments
    @staticmethod
    def echo(**kwargs) -> Dict[str, Any]:
        return kwargs

    def __init__(self, work_type: WorkRequest.WorkType, args: Dict[str, Any], callback: Callable = None):
        super(HapiWorker, self).__init__()
        self.callback = callback
        self.work_type = work_type
        self.args: Dict[str, Any] = args
        self.job_id = HapiWorker.job_id
        HapiWorker.job_id += 1

        self.started.connect(self.__run)

        if self.work_type == WorkRequest.END_WORK_PROCESS:
            end_request = WorkRequest(self.job_id, self.work_type, self.args)
            WorkRequest.WORKQ.put(end_request)
            return
        if self.work_type == WorkRequest.START_HAPI:
            WorkRequest.WORKQ.put(WorkRequest(self.job_id, self.work_type, self.args))
            return
        self.step_signal.connect(lambda x: QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents))

        if callback:
            self.done_signal.connect(self.callback)

    def __run(self):
        work_request = WorkRequest(self.job_id, self.work_type, self.args)
        WorkRequest.WORKQ.put(work_request)

        while True:
            time.sleep(0.01)
            try:
                work_result = WorkRequest.RESULTQ.get_nowait()
                if work_result.job_id == self.job_id:
                    self.done_signal.emit(work_result)
                    return
                HapiWorker.job_results.append(work_result)
            except Exception as e:
                self.step_signal.emit({})
            finally:
                for work_result in HapiWorker.job_results:
                    if work_result.job_id == self.job_id:
                        HapiWorker.job_results.remove(work_result)
                        self.done_signal.emit(work_result.result)
                        return

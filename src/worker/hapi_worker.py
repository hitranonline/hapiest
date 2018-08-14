import time

from PyQt5 import QtWidgets

from worker.hapi_thread import HapiThread
from worker.work_request import *


class HapiWorker(HapiThread):
    """
    A HapiWorker is a part of a work around to Python's GIL (global interpreter lock). Since threads can only run one at
    time in Python, the GUI will freeze even if a worker thread is used. Instead of using threads, separate processes
    are used to separate the calculations form the GUI. The process is a completely separate instance of the python
    interpreter. Data can be sent between the two processes using Queues. These queues, under the hood, work by writing
    serialized python objects to a temp file.

    The HapiWorker object is a way to request work from this worker process, and receive the result from it. Each
    HapiWorker is assigned an id, and will spin until a work result with the same job_id is found.
    """
    job_id: int = 0

    step_signal = QtCore.pyqtSignal(object)
    done_signal = QtCore.pyqtSignal(object)

    job_results: List[WorkResult] = []


    @staticmethod
    def echo(**kwargs) -> Dict[str, Any]:
        """
        *Used to create a map from named arguments.*
        """
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
            self.started.connect(lambda: None)
        elif self.work_type == WorkRequest.START_HAPI:
            WorkRequest.WORKQ.put(WorkRequest(self.job_id, self.work_type, self.args))
            self.started.connect(lambda: None)
        else:
            self.step_signal.connect(lambda x: QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents))
        if callback:
            self.done_signal.connect(self.callback)

    def safe_exit(self):
        self.quit()
        while self.isRunning():
            pass
        return

    def __run(self):
        """
        Attempts to pull results from the result queue until if finds the matching result. The matching result is the
        one that has the same job_id as this HapiWorker object. If it polls a result that does not have the same job_id,
        it places it into a list for other HapiWorkers to check.
        """
        work_request = WorkRequest(self.job_id, self.work_type, self.args)
        WorkRequest.WORKQ.put(work_request)

        while True:
            time.sleep(0.25)
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
                        self.done_signal.emit(work_result)
                        return

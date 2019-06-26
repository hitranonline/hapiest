import os
import unittest
from worker.hapi_worker import *
from worker.work_request import *
from PyQt5.Qt import QApplication

os.chdir('../')
app = QApplication([])
class TestFetch(unittest.TestCase):
    def setUp(self):
        self.workers = []
        WorkRequest.start_work_process()
        self.data_name = 'test' + str(time.time()).replace('.', 'x')

    def worker_done(self, work_result: WorkResult):
        try:
            print("worker_done")
            for worker in self.workers:
                if worker.job_id == work_result.job_id:
                    worker.safe_exit()
                    break
            result = work_result.result
            if result is not None:
                return
        except Exception as e:
            debug(e)
        self.workers.clear()


    def test_worker_fetch(self):
        work = HapiWorker.echo(data_name=self.data_name, iso_id_list=[1],
                               numin=800, numax=1200, parameter_groups=[], parameters=[])
        worker = HapiWorker(WorkRequest.FETCH, work, callback=self.worker_done)
        self.workers.append(worker)
        worker.done_signal.connect(app.exit)
        worker.start()
        self.assertEqual(app.exec_(), 0)


    def tearDown(self) -> None:
        os.chdir('./data')
        for file in os.listdir():
            if file.startswith(self.data_name):
                try:
                    print('Removing: ' + file.title())
                    os.remove(file)
                except OSError:
                    print('f')

if __name__ == '__main__':
    unittest.main()
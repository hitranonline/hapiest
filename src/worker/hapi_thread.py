from PyQt5.QtCore import QThread
from typing import *
from time import sleep


class HapiThread(QThread):
    # A list of all HapiThreads that have been created. This is so when the program exits,
    # all threads can be closed; the threads should be closed safely anyways but in the event that
    # they are not, this will work as a failsafe
    threads: List['HapiThread'] = []

    @staticmethod
    def kill_all():
        for thread in HapiThread.threads:
            if thread == None or thread.isFinished():
                continue
            thread.terminate()
            while thread.isRunning():
                sleep(0.01)
        print('All QThreads have been terminated')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        HapiThread.threads.append(self)

from PyQt5.QtCore import QThread
from typing import *
from time import sleep


class HapiThread(QThread):
    """
    A subclass of QThread that behaves exactly the same, except all threads created are kept track of in a static list.
    This is done so all threads can be terminated cleanly at the end of the program.
    """
    
    
    ## 
    # A list of all HapiThreads that have been created. This is so when the program exits,
    # all threads can be closed; the threads should be closed safely anyways but in the event that
    # they are not, this will work as a failsafe.
    threads: List['HapiThread'] = []


    @staticmethod
    def kill_all():
        """
        A static method that will kill all HapiThreads that have been created.
        """
        for thread in HapiThread.threads:
            if thread == None or thread.isFinished():
                continue
            thread.quit()
            while thread.isRunning():
                sleep(0.01)
        print('All QThreads have been terminated')


    def __init__(self, *args, **kwargs):
        """
        Calls the super constructor and adds 'self' to the static list of all HapiThreads
        """
        super().__init__(*args, **kwargs)
        HapiThread.threads.append(self)

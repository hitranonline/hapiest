import os
import sys
import functools
import traceback
import multiprocessing as mp
from typing import Dict, List, Tuple, Union, Any, Optional, Callable

from hapi import *
from utils.fetch_error import FetchErrorKind, FetchError
from utils.graphing.band import Band, Bands
from utils.hapiest_util import echo
from utils.log import *
from utils.metadata.config import Config
from utils.metadata.hapi_metadata import HapiMetaData
from utils.xsc import CrossSection
from worker.work_result import WorkResult
from worker.work_functions import WorkFunctions

class WorkRequest:
    def __init__(self, job_id: int, work_type: Any, work_args: Dict[str, Any]):
        self.job_id = job_id
        self.work_type = work_type
        self.work_args = work_args

    WorkType = int
    
    # A list of "opcodes," rather than using strings
    START_HAPI: WorkType = 0
    END_WORK_PROCESS: WorkType = 1
    FETCH: WorkType = 2
    ABSORPTION_COEFFICIENT: WorkType = 3
    TABLE_META_DATA: WorkType = 4
    GET_TABLE: WorkType = 5
    SAVE_TABLE: WorkType = 6
    TABLE_NAMES: WorkType = 7
    SELECT: WorkType = 8
    TRANSMITTANCE_SPECTRUM: WorkType = 9
    RADIANCE_SPECTRUM: WorkType = 10
    ABSORPTION_SPECTRUM: WorkType = 11
    BANDS: WorkType = 12
    DOWNLOAD_XSCS: WorkType = 13

    WORKQ: mp.Queue = mp.Queue()
    RESULTQ: mp.Queue = mp.Queue()

    WORKER: 'Work' = None

    WORK_FUNCTIONS: Dict[WorkType, Callable] = {}

    def do_work(self) -> Any:
        """
        Executes the appropriate function, based on the specified work_type in the work request.
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
        Handles the calling of most hapi functions.
        """
        WorkRequest.WORK_FUNCTIONS = {
            WorkRequest.START_HAPI: WorkFunctions.start_hapi,
            WorkRequest.FETCH: WorkFunctions.fetch,
            WorkRequest.ABSORPTION_COEFFICIENT: WorkFunctions.graph_absorption_coefficient,
            WorkRequest.GET_TABLE: WorkFunctions.get_table,
            WorkRequest.SAVE_TABLE: WorkFunctions.save_table,
            WorkRequest.TABLE_NAMES: WorkFunctions.table_names,
            WorkRequest.TABLE_META_DATA: WorkFunctions.table_meta_data,
            WorkRequest.SELECT: WorkFunctions.select,
            WorkRequest.ABSORPTION_SPECTRUM: WorkFunctions.graph_absorption_spectrum,
            WorkRequest.TRANSMITTANCE_SPECTRUM: WorkFunctions.graph_transmittance_spectrum,
            WorkRequest.RADIANCE_SPECTRUM: WorkFunctions.graph_radiance_spectrum,
            WorkRequest.BANDS: WorkFunctions.graph_bands,
            WorkRequest.DOWNLOAD_XSCS: WorkFunctions.download_xscs
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

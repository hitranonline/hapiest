from typing import *


class WorkResult:
    def __init__(self, job_id: int, result: Any):
        self.job_id = job_id
        self.result = result

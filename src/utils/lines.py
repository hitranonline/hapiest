from typing import *
import time

from utils.log import *
from worker.hapi_worker import HapiWorker
from worker.work_result import WorkResult
from worker.work_request import WorkRequest


class Lines:
    def __init__(self, table_name: str, parameters: Dict[str, List[Union[int, float]]], page_number: int, page_len: int,
                 last_page: int, **kwargs):
        self.last_page = last_page
        self.table_name = table_name
        self.page_number: int = page_number
        self.page_len: int = page_len
        self.parameters: Dict[str, List[Union[int, float]]] = parameters
        self.param_order = []

        self.workers: List['HapiWorker'] = []

        for (param_name, param_list) in parameters.items():
            self.entries: int = len(param_list)
            self.param_order.append(param_name)
        self.param_order = tuple(self.param_order)

    def get_len(self):
        for (k, v) in self.parameters.items():
            return len(v)

    def get_line(self, line_number: int) -> Optional['Line']:
        if self.entries <= line_number:
            return None
        line = []
        for param in self.param_order:
            line.append(self.parameters[param][line_number])

        l = Line(line_number, line, self)
        return l

    def update_line_field(self, line: 'Line', field_index: int):
        self.parameters[self.param_order[field_index]][line.line_number] = line.line[field_index]

    def commit_changes(self):
        start_index = self.page_len * self.page_number
        args = HapiWorker.echo(
            table_name=self.table_name,
            start_index=start_index,
            data=self.parameters
        )
        worker = HapiWorker(WorkRequest.TABLE_COMMIT_LINES_PAGE, args, self.commit_done)
        self.workers.append(worker)
        worker.start()
        log("Committing lines {0} - {1} to table {2}.".format(start_index, start_index + self.page_len,
                                                              self.table_name))

    def commit_done(self, work_result: 'WorkResult'):
        if not work_result:
            err_log("Failed to commit to table {0}.".format(self.table_name))
            return
        log("Successfully committed to table {0}.".format(self.table_name))

        for worker in self.workers:
            if worker.job_id == work_result.job_id:
                worker.safe_exit()
                self.workers.remove(worker)
                break

class Line:
    def __init__(self, line_number: int, line: List[Union[int, float]], lines: 'Lines'):
        self.line_number = line_number
        self.line = line
        self.lines = lines

    def update_nth_field(self, field_index: int, new_value: Union[int, float]):
        self.line[field_index] = new_value
        self.lines.update_line_field(self, field_index)

    def get_nth_field(self, field_index: int) -> Union[int, float]:
        return self.line[field_index]

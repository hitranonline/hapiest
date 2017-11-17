from typing import *
from utils.log import *
from worker.hapi_worker import *
from worker.work_request import *


class Lines:
    def __init__(self, table_name: str, parameters: Dict[str, List[Union[int, float]]], page: int, page_len: int = 20,
                 last_page: int = False):
        self.table_name = table_name
        self.page: int = page
        self.page_len: int = page_len
        self.parameters: Dict[str, List[Union[int, float]]] = parameters
        self.param_order = []

        self.workers: List[HapiWorker] = []

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
        return Line(line_number, line, self)

    def update_line_field(self, line: 'Line', field_index: int):
        self.parameters[self.param_order[field_index]][line.line_number] = line.line[field_index]

    def commit_changes(self):
        start_index = self.page_len * self.page,
        args = HapiWorker.echo(
            table_name=self.table_name,
            start_index=start_index,
            data=self.parameters,
        )
        worker = HapiWorker(WorkRequest.TABLE_COMMIT_LINES_PAGE, args, self.commit_done)
        self.workers.append(worker)
        worker.start()
        log("Committing lines {0} - {1} to table {2}.".format(start_index, start_index + self.page_len,
                                                              self.table_name))

    def commit_done(self, work_result: WorkResult):
        log("Successfully committed to table {0}.".format(self.table_name))
        for worker in self.workers:
            if worker.job_id == work_result.job_id:
                worker.exit()
                self.workers.remove(worker)
            break


class Line:
    def __init__(self, line_number: int, line: List[Union[int, float]], lines: 'Lines'):
        self.line_number = line_number
        self.line = line
        self.lines = lines

    def update_nth_field(self, field_index: int, new_value: Union[int, float]):
        self.line[field_index] = new_value
        self.lines.update_line_field(self)

    def get_nth_field(self, field_index: int) -> Union[int, float]:
        return self.line[field_index]

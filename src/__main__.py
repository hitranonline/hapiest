from PyQt5 import QtWidgets, QtCore
from main_window import *
from worker import *
import hapiest_util


def main():
    if Config.high_dpi == 'true':
        # Enable High DPI display with PyQt5
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()

    window.gui.adjustSize()
    window.gui.setFixedSize(window.gui.size())

    init_console_redirect(window, sys.argv)

    Work.start_work_process()

    start = HapiWorker(HapiWorker.echo(type=Work.START_HAPI))
    start.start()

    # Exit code
    qt_result = app.exec_()

    util_close()

    close = HapiWorker(HapiWorker.echo(type=Work.END_WORK_PROCESS))

    sys.exit(qt_result)


if __name__ == '__main__':
    main()

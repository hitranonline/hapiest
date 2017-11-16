from utils.console_redirect import *
import sys


def print_html_to_status_bar(arg):
    TextReceiver.TEXT_EDIT_STREAM.write_html(arg)


# A binding to the print function that prints to stderr rather than stdout, since stdout gets redirected into a gui
# element
def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# Prints to the console_output with a fancy lookin log label
def log(arg):
    print_html_to_status_bar('<div style="color: #7878e2">[Log]</div>&nbsp;' + arg)
    print("[Log] ", arg, file=sys.__stdout__)


# Prints to the console_output with a fancy lookin error label
def err_log(dat):
    print_html_to_status_bar('<div style="color: #e27878">[Error]</div>&nbsp;' + dat)
    print("[Err] ", dat, file=sys.__stdout__)


def debug_log(dat):
    print_html_to_status_bar('<div style="color: #78e278">[Debug]</div>&nbsp;' + dat)
    print("[Log] ", dat, file=sys.__stdout__)

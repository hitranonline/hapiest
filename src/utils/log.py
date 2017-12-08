from utils.console_redirect import *
import sys


def print_html_to_status_bar(arg):
    TextReceiver.TEXT_EDIT_STREAM.write_html(arg)



def debug(*args, **kwargs):
    """
    * A binding to the print function that prints to stderr rather than stdout, since stdout gets redirected into a gui element.*
    """
    print(*args, file=sys.stderr, **kwargs)



def log(arg):
    """
    *Prints to the console_output with a fancy lookin log label.*
    """
    print_html_to_status_bar('<div style="color: #7878e2">[Log]</div>&nbsp;' + arg)
    print("[Log] ", arg, file=sys.__stdout__)


def err_log(dat):
    """
    *Prints to the console_output with a fancy lookin error label.*
    """
    print_html_to_status_bar('<div style="color: #e27878">[Error]</div>&nbsp;' + dat)
    print("[Err] ", dat, file=sys.__stdout__)


def debug_log(dat):
    """
    *prints error to status bar.*
    """
    print_html_to_status_bar('<div style="color: #78e278">[Debug]</div>&nbsp;' + dat)
    print("[Log] ", dat, file=sys.__stdout__)

#!/usr/bin/env python

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    ORANGE = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    LGRAY = '\033[0;37m'
    DGRAY = '\033[1;30m'
    LRED = '\033[1;31m'
    LGREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    LBLUE = '\033[1;34m'
    LPURPLE = '\033[1;35m'
    LCYAN = '\033[1;36m'
    WHITE = '\033[1;37m'
    Error = '\033[0;31m'
    Warning = '\033[0;33m'
    Info = '\033[0;34m'
    Success = '\033[0;32m'
    Reset = '\033[0;39m'


def print_color(color, message):
    print(f'{color}{message}{Colors.Reset}')


def print_info(message):
    print('\033[34m{}\033[0m'.format(message))


def print_warn(message):
    print('\033[93m{}\033[0m'.format(message))


def print_error(message):
    print('\033[91m{}\033[0m'.format(message))


def confirm(question):
    while True:
        answer = input(f'{question} [Y/n]: ').lower()
        if answer == 'y' or answer == 'yes':
            return True
        if answer == 'n' or answer == 'no':
            return False
        print('I did not quite catch that! Please answer yes or no.')

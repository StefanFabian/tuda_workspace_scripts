#!/usr/bin/env python

def info(message):
    print('\033[34m{}\033[0m'.format(message))


def warn(message):
    print('\033[93m{}\033[0m'.format(message))


def error(message):
    print('\033[91m{}\033[0m'.format(message))


def confirm(question):
    while True:
        answer = input(f'{question} [Y/n]: ').lower()
        if answer == 'y' or answer == 'yes':
            return True
        if answer == 'n' or answer == 'no':
            return False
        print('I did not quite catch that! Please answer yes or no.')

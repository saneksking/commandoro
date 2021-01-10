#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Licensed under the terms of the BSD 3-Clause License
# (see LICENSE for details)
# Copyright © 2020-2021 Aleksandr Suvorov
# -----------------------------------------------------------------------------
"""
Console utility for automatic command execution

Store commands for different tasks or systems in one
place and execute them automatically.

The console version allows you to run a script in the terminal,
passing it a file with settings as an argument,
or use the default file. In the process, you select the desired
command package, then you can start execution,
display a list of commands for this package,
or return to the selection of the command package.

After executing all the commands,
the program goes to the main menu and again waits for
input to select the desired package, or exit the program.
"""
import click
import inspect
import json
import os
import shutil

__version__ = '0.0.7a'
__author__ = 'Aleksandr Suvorov'
__description__ = 'CLI utility for automatic command execution'
__url__ = 'https://githib.com/mysmarthub'
__donate__ = 'Donate: https://yoomoney.ru/to/4100115206129186'
__copyright__ = 'Copyright © 2020-2021 Aleksandr Suvorov'


class Pack:
    def __init__(self, name, command_list):
        self.name = name
        self.command_list = command_list

    @property
    def count(self):
        return len(self.command_list)


def executor(command: str, test: bool = False) -> bool:
    """
    Executes the command

    :param command: <str> Command to execute
    :param test: <bool> Used for testing. True disables the actual execution of commands.
    :return: <bool> Logical status of command execution
    """
    if not test:
        if type(command) is str:
            status = os.system(command)
            if status:
                return False
    return True


def open_file(file):
    """
    Open the settings file in json format.

    :param file: <str> Path to the file in json format with command packages
    :return: <dict> Dictionary with command packages, where the key is the name of the package,
    and the value is a list of commands. If an error occurs, it returns an empty dictionary.
    """
    try:
        with open(file, 'r') as f:
            json_data = json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return {}
    else:
        return json_data


def smart_print(text='', char='-'):
    if not char:
        char = ' '
    columns, _ = shutil.get_terminal_size()
    if text:
        print(f' {text} '.center(columns, char))
    else:
        print(f''.center(columns, char))


def start_logo():
    smart_print('', '*')
    smart_print(f'Commandoro {__version__} | Author: {__author__}', '=')
    smart_print(f'{__description__}', ' ')
    smart_print()


def end_logo():
    smart_print('Program completed', '-')
    smart_print(f'{__donate__}', '-')
    smart_print(f'https://www.paypal.com/paypalme/myhackband', '-')
    smart_print(f'{__copyright__}', '=')


def get_pack_name(pack_objects: dict):
    num_pack = {n: name for n, name in enumerate(pack_objects.keys(), 1)}
    while 1:
        """Shows a simple menu."""
        smart_print('Command packages:')
        for n, name in num_pack.items():
            print(f'{n}. {name} | Commands[{pack_objects[name].count}]')
        smart_print()
        num = click.prompt(text='Enter the package number and click Enter '
                                '(ctrl+c to exit): ', type=int)
        pack_name = num_pack[num]
        command_list = pack_objects[pack_name].command_list
        if num not in num_pack:
            print('Input Error!')
            continue
        while 1:
            smart_print()
            print(f'The selected package {num_pack[num]} | Commands:[{pack_objects[pack_name].count}]')
            smart_print()
            print('1. Start')
            print('2. Show commands')
            print('3. Cancel')
            smart_print()
            user_input = click.prompt(text='Enter the desired number and press ENTER: ', type=int)
            smart_print()
            if user_input not in (1, 2, 3):
                print('Input Error!')
            elif user_input == 1:
                return pack_name
            elif user_input == 2:
                click.echo()
                click.echo(f'{pack_name} commands: ')
                for command in command_list:
                    print(command)
                continue
            break


def start(pack_obj, test=False):
    count = 0
    errors = []
    click.echo()
    click.echo(f'Pack name: [{pack_obj.name}]')
    smart_print()
    for command in pack_obj.command_list:
        count += 1
        click.echo()
        msg = f'[execute {count}]: {command}'
        click.echo(msg)
        status = executor(command, test=test)
        if status:
            print('[Successfully]')
        else:
            errors.append(f'Error: {msg}')
            print('[Error]')
        smart_print()
    smart_print('', '=')
    click.echo(f'The command package [{pack_obj.name}] is executed.')
    click.echo(f'Commands completed: [{count - len(errors)}] | Errors: [{len(errors)}]')


@click.command()
@click.option('--file', '-f', help='The path to the file with the command packs')
@click.option('--default', '-d', is_flag=True, help='Run an additional batch of commands from default')
@click.option('--test', '-t', is_flag=True, help='Test run, commands will not be executed.')
@click.option('--name', '-n', help='Name of the package to run automatically')
def cli(file, default, name, test):
    """Commandoro - CLI utility for automatic command execution

    - To work, it uses files that store named command packages,
        where the name is the name of the command package,
        and the value is a list of commands.

        You can create your own files with command packages using
            the default structure.

    - Use the default name for the package with the default commands.
        You can perform them in addition to the selected command package.

    - You can pass the file name as an argument,
        or use the default file, it should be located
        in the same directory as the file being run.

    -The console version allows you to run a script in the terminal,
        passing it a file with settings as an argument,
        or use the default file. In the process, you select the desired
        command package, then you can start execution,
        display a list of commands for this package,
        or return to the selection of the command package.

    - After executing all the commands,
        the program goes to the main menu and again waits for
        input to select the desired package, or exit the program.

    - You can pass the name of the desired package,
        and if it exists inside the file with the command settings from it
        will be executed.

    - The examples run:

    python commandoro.py --file=config.json -d

    python commandoro.py --file=config.json -d --name=Ubuntu

    """
    start_logo()
    if os.path.exists(str(file)):
        file = file
    else:
        click.echo('The path is not found, we are looking for the default file...')
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        folder = os.path.dirname(os.path.abspath(filename))
        file = os.path.join(folder, 'config.json')
    if file:
        pack_dict = open_file(file)
        pack_objects = {key: Pack(name=key, command_list=val) for key, val in pack_dict.items()}
        if pack_dict:
            if name and name in pack_dict:
                pack_name = name
            else:
                pack_name = get_pack_name(pack_objects)
            pack_obj = Pack(pack_name, pack_dict[pack_name])
            start(pack_obj, test=test)
            if default and 'default' in pack_dict and pack_name != 'default':
                pack_obj = Pack(name='default', command_list=pack_dict['default'])
                start(pack_obj=pack_obj, test=test)
        else:
            click.echo('No data available...')
    else:
        click.echo('Failed to load settings...')
    end_logo()


if __name__ == '__main__':
    cli()

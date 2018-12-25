import os
import readline  # noqa
import sys
from functools import partial
from json import dump, loads
from time import time as now

from datadispatch import datadispatch
from pkg_resources import get_distribution

from . import commands, events
from .color import no_color, shell_color
from .model import initial_state, render
from .update import update

_COLOR = shell_color if sys.stdout.isatty() else no_color
_STORE = os.getenv(
    'TASKS_STORE', os.path.join(os.getenv('HOME'), '.tasks.json'))


def run():
    if len(sys.argv) > 1:
        _non_interactive(' '.join(sys.argv[1:]))
    else:
        _interactive(get_distribution('tasks').version)


def _non_interactive(input_):
    _handle_event(update, _state(), events.input_read(input_))


def _interactive(version):
    state = _handle_event(update, _state(), events.initialized(version))

    try:
        while True:
            state = _handle_event(update, state, events.input_read(input(
                '{} '.format(render(state)))))
    except (EOFError, KeyboardInterrupt):
        print()


def _state():
    state = initial_state()

    for event in _load():
        state, _ = update(state, event, event['time'])

    return state


def _load():
    if not os.path.exists(_STORE):
        raise StopIteration

    with open(_STORE) as f:
        for line in f:
            yield loads(line)


def _handle_event(update_func, state, event):
    state, commands = update_func(state, event, now())

    for command in commands:
        state = _handle_command(
            partial(_handle_event, update_func), state, command)

    return state


@datadispatch(lambda args, _: args[2].get('type'))
def _handle_command(event_handler, command):
    raise ValueError('bad command: {}'.format(command.get('type')))


@_handle_command.register(commands.PRINTLN)
def _handle_println(event_handler, state, command):
    for line in command['lines']:
        print(_COLOR(line))

    return state


@_handle_command.register(commands.STORE)
def _handle_store(event_handler, state, command):
    event = {'time': now(), **command['event']}
    with open(_STORE, 'a') as f:
        dump(event, f)
        f.write('\n')

    return event_handler(state, event)


@_handle_command.register(commands.EDITOR)
def _handle_editor(event_handler, state, command):
    path = os.path.join('/tmp', 'tasks.{}.edit'.format(os.getpid()))

    open(path, 'w').write(command['content'])
    os.system('{} {}'.format(os.getenv('EDITOR', 'editor'), path))
    edited = open(path).read()

    os.remove(path)

    if edited != command['content']:
        return event_handler(state, command['edited_func'](edited))

    return state

import os
import readline  # noqa
from functools import partial
from json import dump, loads
from time import time as now

from . import commands, events
from .color import shell_color
from .func import valuedispatch
from .model import initial_state, render
from .update import update

STORE = os.getenv(
    'TASKS_STORE', os.path.join(os.getenv('HOME'), '.tasks.json'))


def run():
    state = initial_state()

    for event in _load():
        state, _ = update(state, event, event['time'])

    state = _handle_event(update, state, events.initialized())

    try:
        while True:
            state = _handle_event(update, state, events.input_read(input(
                '{} '.format(render(state)))))
    except (EOFError, KeyboardInterrupt):
        print()


def _load():
    if not os.path.exists(STORE):
        raise StopIteration

    with open(STORE) as f:
        for line in f:
            yield loads(line)


def _handle_event(update_func, state, event):
    state, commands = update_func(state, event, now())

    for command in commands:
        state = _handle_command(
            partial(_handle_event, update_func), state, command)

    return state


@valuedispatch(lambda args, _: args[2].get('type'))
def _handle_command(event_handler, command):
    raise ValueError('bad command: {}'.format(command.get('type')))


@_handle_command.register(commands.PRINTLN)
def _handle_println(event_handler, state, command):
    for line in command['lines']:
        print(shell_color(line))

    return state


@_handle_command.register(commands.STORE)
def _handle_store(event_handler, state, command):
    event = {'time': now(), **command['event']}
    with open(STORE, 'a') as f:
        dump(event, f)
        f.write('\n')

    return event_handler(state, event)


@_handle_command.register(commands.EDITOR)
def _handle_editor(event_handler, state, command):
    path = os.path.join('/tmp', 'tasks.{}.edit'.format(os.getpid()))

    open(path, 'w').write(command['content'])
    os.system('editor {}'.format(path))
    edited = open(path).read()

    os.remove(path)

    if edited != command['content']:
        return event_handler(state, command['edited_func'](edited))

    return state

from itertools import chain

from . import commands, events
from .func import valuedispatch


def initial_state():
    return {
        'items': [],
        'selected': 0,
        'last_num': 0,
    }


def render(state):
    if state['selected']:
        return '#{}>'.format(state['selected'])
    else:
        return '>'


@valuedispatch(lambda args, _: args[1].get('type'))
def update(state, event, time):
    raise ValueError('bad event: {}'.format(event.get('type')))


@update.register(events.INITIALIZED)
def _update_initialized(state, event, time):
    return state, [commands.println([
        'Welcome to tasks',
        'type help for help, exit with ^D or ^C',
    ])]


@update.register(events.ITEM_ADDED)
def _update_item_added(state, event, time):
    s = {
        **state,
        'items': [*state['items'], event['item']],
        'last_num': event['item']['num'],
        'selected': state['selected'] or event['item']['num'],
    }

    return s, _notify_change(state, s)


@update.register(events.INPUT_READ)
def _update_input(state, event, time):
    return _parse(state, event['input'], time)


@valuedispatch(lambda args, _: args[1].split(' ', 1)[0])
def _parse(state, input_, time):
    return state, [commands.println('unknown command, try "help"')]


@_parse.register('add')
def _parse_add(state, input_, time):
    parts = input_.split(' ', 1)
    event = events.item_added(1 + state['last_num'], parts[1])
    return state, [
        commands.println('added {}'.format(_fmt_item(event['item']))),
        commands.store(event),
    ]


def _fmt_item(item):
    return '#{} {} {}'.format(item['num'], item['status'], item['text'])


def _notify_change(before, after):
    if before['selected'] == after['selected']:
        return []
    if not after['selected']:
        return []

    item = _find(after['items'], after['selected'])
    return [commands.println('now on {}'.format(_fmt_item(item)))]


def _iter_status(items, status):
    return (item for item in items if item['status'] == status)


def _iter_backlog(items):
    return chain(
        _iter_status(items, events.STATUS_PROGRESS),
        _iter_status(items, events.STATUS_TODO),
    )


def _find(items, num):
    return next((item for item in items if item['num'] == num), None)

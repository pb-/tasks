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


@update.register(events.ITEM_STARTED)
def _update_item_started(state, event, time):
    return _update_status(state, event['num'], events.STATUS_PROGRESS)


@update.register(events.ITEM_DONE)
def _update_item_done(state, event, time):
    return _update_status(state, event['num'], events.STATUS_DONE)


@update.register(events.ITEM_DELETED)
def _update_item_done(state, event, time):
    return _update_status(state, event['num'], events.STATUS_DELETED)


@update.register(events.ITEM_BLOCKED)
def _update_item_done(state, event, time):
    return _update_status(state, event['num'], events.STATUS_BLOCKED)


def _update_status(state, num, status):
    items = [{
        **item,
        'status': status,
    } if item['num'] == num else item for item in state['items']]

    s = {
        **state,
        'items': items,
        'selected': (
            num if status == events.STATUS_PROGRESS else _next_selection(items)
        ),
    }

    return s, _notify_change(state, s)


@update.register(events.INPUT_READ)
def _update_input(state, event, time):
    parts = event['input'].strip().split(' ', 1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ''
    return _parse(state, cmd, args, time)


@valuedispatch(lambda args, _: args[1])
def _parse(state, cmd, args, time):
    return state, [commands.println('unknown command, try "help"')]


@_parse.register('a')
@_parse.register('add')
def _parse_add(state, _, args, time):
    event = events.item_added(1 + state['last_num'], args)
    return state, [
        commands.println('added {}'.format(_fmt_item(event['item']))),
        commands.store(event),
    ]


@_parse.register('bl')
@_parse.register('backlog')
def _parse_backlog(state, _, args, time):
    return state, map(
        commands.println, map(_fmt_item, _iter_backlog(state['items'])))


@_parse.register('s')
@_parse.register('start')
def _parse_start(state, _, args, time):
    if not state['selected']:
        return state, [commands.println('nothing to start')]

    return state, [commands.store(events.item_started(state['selected']))]


@_parse.register('d')
@_parse.register('done')
def _parse_done(state, _, args, time):
    if not state['selected']:
        return state, [commands.println('nothing to complete')]

    return state, [commands.store(events.item_done(state['selected']))]


@_parse.register('x')
@_parse.register('delete')
def _parse_done(state, _, args, time):
    if not state['selected']:
        return state, [commands.println('nothing to delete')]

    return state, [commands.store(events.item_deleted(state['selected']))]


@_parse.register('blocked')
def _parse_done(state, _, args, time):
    if not state['selected']:
        return state, [commands.println('nothing to block')]

    return state, [commands.store(events.item_blocked(state['selected']))]


def _fmt_item(item):
    return '#{} {} {}'.format(item['num'], item['status'], item['text'])


def _next_selection(items):
    return next(_iter_backlog(items), {'num': 0})['num']


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

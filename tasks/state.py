from itertools import chain

from . import commands, events
from .func import valuedispatch
from .color import escape


def initial_state():
    return {
        'items': [],
        'selected': 0,
        'last_num': 0,
    }


def render(state):
    if state['selected']:
        item = _find(state['items'], state['selected'])
        return '#{}({})>'.format(state['selected'], item['status'][0])
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


@update.register(events.ITEM_STATUS_CHANGED)
def _update_status_changed(state, event, time):
    status = event['status']
    num = event['num']
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


@_parse.register('st')
@_parse.register('status')
def _parse_status(state, _, args, time):
    if not state['selected']:
        return state, [commands.println('no item selected')]

    return state, [commands.println('currently on {}'.format(
        _fmt_item(_find(state['items'], state['selected']))))]


@_parse.register('bl')
@_parse.register('backlog')
def _parse_backlog(state, _, args, time):
    return _list(state, _iter_backlog)


@_parse.register('all')
def _parse_all(state, _, args, time):
    return _list(state, _iter_all)


def _list(state, iterator):
    return state, map(
        commands.println, map(_fmt_item, iterator(state['items'])))


@_parse.register('s')
@_parse.register('start')
@_parse.register('d')
@_parse.register('done')
@_parse.register('x')
@_parse.register('delete')
@_parse.register('blocked')
def _parse_status(state, cmd, args, time):
    if not state['selected']:
        return state, [commands.println('no item selected')]

    status = {
        's': events.STATUS_PROGRESS,
        'start': events.STATUS_PROGRESS,
        'd': events.STATUS_DONE,
        'done': events.STATUS_DONE,
        'x': events.STATUS_DELETED,
        'delete': events.STATUS_DELETED,
        'blocked': events.STATUS_BLOCKED,
    }.get(cmd)

    return state, [commands.store(events.item_status_changed(
        state['selected'], status))]


def _fmt_item(item, color=True):
    color = {
        events.STATUS_TODO: 'blue',
        events.STATUS_PROGRESS: 'yellow',
        events.STATUS_DONE: 'green',
        events.STATUS_BLOCKED: 'red',
        events.STATUS_DELETED: 'normal',
    }.get(item['status'])

    return '[gray #{}] [{} {}] [white {}]'.format(
        item['num'], color, item['status'], escape(item['text']))


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


def _iter_all(items):
    return chain(
        _iter_backlog(items),
        _iter_status(items, events.STATUS_BLOCKED),
        _iter_status(items, events.STATUS_DONE),
        _iter_status(items, events.STATUS_DELETED),
    )


def _find(items, num):
    return next((item for item in items if item['num'] == num), None)

import re
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

    with_items = {
        **state,
        'items': items,
    }

    with_selected = {
        **with_items,
        'selected': _next_selection(with_items, num, status),
    }

    return with_selected, _notify_change(state, with_selected)


def _next_selection(state, num, status):
    """num has just moved to status, decide on next num."""
    if status == events.STATUS_PROGRESS:
        return num

    if not state['selected']:
        return _next_backlog_num(state['items'])

    item = _find(state['items'], state['selected'])
    if item['status'] == events.STATUS_PROGRESS:
        return state['selected']

    return _next_backlog_num(state['items'])


@update.register(events.ITEM_ORDER_EDITED)
def _update_order_edited(state, event, time):
    match = re.compile(r'^\s*#(?P<num>\d+)').match
    lines = event['content'].strip().split('\n')
    nums = [int(match(line).group('num')) for line in lines if match(line)]

    if not all(_find(state['items'], num) for num in nums):
        return state, []

    return state, [commands.store(events.items_reordered(nums))]


@update.register(events.ITEMS_REORDERED)
def _update_reordered(state, event, time):
    ordered = [
        i for num in event['nums'] for i in state['items'] if i['num'] == num]
    rest = [i for i in state['items'] if i['num'] not in event['nums']]

    with_items = {
        **state,
        'items': ordered + rest,
    }

    with_selected = {
        **with_items,
        'selected': _next_backlog_num(with_items['items']),
    }

    return with_selected, [
        commands.println('order updated'),
        *_notify_change(state, with_selected)]


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
    items = list(iterator(state['items']))
    if not items:
        return state, []

    max_len = max(_item_len(state, item) for item in items)

    return state, [
        commands.println('{}{}{}'.format(
            ' ' * (max_len - _item_len(state, item)),
            '*' if item['num'] == state['selected'] else '', _fmt_item(item)))
        for item in items
    ]


def _item_len(state, item):
    return len(str(item['num'])) + int(item['num'] == state['selected'])


@_parse.register('order')
def _parse_order(state, _, args, time):
    content = ''.join(
        '#{} {}\n'.format(item['num'], item['text'])
        for item in _iter_status(state['items'], events.STATUS_TODO))

    return state, [commands.editor(content, events.item_order_edited)]


@_parse.register('s')
@_parse.register('start')
@_parse.register('d')
@_parse.register('done')
@_parse.register('x')
@_parse.register('delete')
@_parse.register('blocked')
def _parse_status_change(state, cmd, args, time):
    num = _parse_num(args)
    if args:
        if not num:
            return state, [commands.println('bad item num')]

        if not _find(state['items'], num):
            return state, [commands.println('bad item')]

    if not num and not state['selected']:
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
        num or state['selected'], status))]


def _parse_num(s):
    try:
        return int(s)
    except ValueError:
        return None


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


def _next_backlog_num(items):
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

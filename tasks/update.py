import re

from datadispatch import datadispatch

from . import commands, events, model
from .parse import parse_input


def update(state, event, time):
    after, cmds = _with_undo(state, event, time)
    return after, cmds + _notify_change(state, after)


def _with_undo(state, event, time):
    after, cmds = _update(state, event, time)

    if state == after or event.get('type') == events.UNDONE:
        return after, cmds

    return {**after, 'prev': _prune_prev(state, 10)}, cmds


def _prune_prev(state, depth):
    if not state or not depth:
        return None

    prev = _prune_prev(state['prev'], depth - 1)

    return {**state, 'prev': prev}


@datadispatch(lambda args, _: args[1].get('type'))
def _update(state, event, time):
    raise ValueError('bad event: {}'.format(event.get('type')))


@_update.register(events.UNDONE)
def _update_undo(state, event, time):
    return state['prev'], []


@_update.register(events.INITIALIZED)
def _update_initialized(state, event, time):
    return state, [commands.println([
        'Welcome to tasks {}'.format(event['version']),
        'type help for help, intro for an introduction, and exit with ^D or ^C'
    ])]


@_update.register(events.ITEM_ADDED)
def _update_item_added(state, event, time):
    s = {
        **state,
        'items':
            [event['item'], *state['items']] if event.get('position') == 'top'
            else [*state['items'], event['item']],
        'last_num': event['item']['num'],
    }

    return {
        **s,
        'selected': _next_selection(
            s, event['item']['num'], event['item']['status']),
    }, []


@_update.register(events.ITEM_STATUS_CHANGED)
def _update_status_changed(state, event, time):
    status = event['status']
    num = event['num']
    items = [{
        **item,
        'status': status,
        '{}_at'.format(status): event['time'],
    } if item['num'] == num else item for item in state['items']]

    with_items = {
        **state,
        'items': items,
    }

    return {
        **with_items,
        'selected': _next_selection(with_items, num, status),
    }, []


def _next_selection(state, num, status):
    """num has just moved to status, decide on next num."""
    if status == events.STATUS_PROGRESS:
        return num

    if not state['selected']:
        return model.next_backlog_num(state['items'])

    item = model.find(state['items'], state['selected'])
    if item['status'] == events.STATUS_PROGRESS:
        return state['selected']

    return model.next_backlog_num(state['items'])


@_update.register(events.ITEM_ORDER_EDITED)
def _update_order_edited(state, event, time):
    match = re.compile(r'^\s*#(?P<num>\d+)').match
    lines = event['content'].strip().split('\n')
    nums = [int(match(line).group('num')) for line in lines if match(line)]

    if not all(model.find(state['items'], num) for num in nums):
        return state, []

    return state, [commands.store(events.items_reordered(nums))]


@_update.register(events.ITEMS_REORDERED)
def _update_reordered(state, event, time):
    ordered = [
        i for num in event['nums'] for i in state['items'] if i['num'] == num]
    rest = [i for i in state['items'] if i['num'] not in event['nums']]

    with_items = {
        **state,
        'items': ordered + rest,
    }

    return {
        **with_items,
        'selected': model.next_backlog_num(with_items['items']),
    }, [commands.println('order updated')]


@_update.register(events.ITEM_EDIT_REQUESTED)
def _update_item_edit_requested(state, event, time):
    text = event['text'].strip()
    if not text:
        return state, []

    return state, [commands.store(events.item_edited(event['num'], text))]


@_update.register(events.ITEM_EDITED)
def _update_item_edited(state, event, time):
    return {
        **state,
        'items': [{
            **item,
            'text': event['text'],
        } if item['num'] == event['num'] else item for item in state['items']],
    }, [commands.println('item updated')]


@_update.register(events.INPUT_READ)
def _update_input(state, event, time):
    return state, parse_input(state, event['input'].strip(), time)


def _notify_change(before, after):
    if before['selected'] == after['selected']:
        return []
    if not after['selected']:
        return []

    item = model.find(after['items'], after['selected'])
    return [commands.println('now on {}'.format(model.fmt_item(item)))]

import re

from . import commands, events, model
from .func import valuedispatch
from .parse import parse_input


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
        '{}_at'.format(status): event['time'],
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
        return model.next_backlog_num(state['items'])

    item = model.find(state['items'], state['selected'])
    if item['status'] == events.STATUS_PROGRESS:
        return state['selected']

    return model.next_backlog_num(state['items'])


@update.register(events.ITEM_ORDER_EDITED)
def _update_order_edited(state, event, time):
    match = re.compile(r'^\s*#(?P<num>\d+)').match
    lines = event['content'].strip().split('\n')
    nums = [int(match(line).group('num')) for line in lines if match(line)]

    if not all(model.find(state['items'], num) for num in nums):
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
        'selected': model.next_backlog_num(with_items['items']),
    }

    return with_selected, [
        commands.println('order updated'),
        *_notify_change(state, with_selected)]


@update.register(events.INPUT_READ)
def _update_input(state, event, time):
    return state, parse_input(state, event['input'].strip(), time)


def _notify_change(before, after):
    if before['selected'] == after['selected']:
        return []
    if not after['selected']:
        return []

    item = model.find(after['items'], after['selected'])
    return [commands.println('now on {}'.format(model.fmt_item(item)))]

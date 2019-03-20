from itertools import chain

from . import events
from .color import escape


def initial_state():
    return {
        'items': [],
        'selected': 0,
        'last_num': 0,
        'prev': None,
    }


def render(state):
    block = '!' if next(
        iter_status(state['items'], events.STATUS_BLOCKED), None) else ''

    if state['selected']:
        item = find(state['items'], state['selected'])
        return '#{}({}){}>'.format(state['selected'], item['status'][0], block)
    else:
        return '{}>'.format(block)


def find(items, num):
    return next((item for item in items if item['num'] == num), None)


def next_backlog_num(items):
    return next(iter_backlog(items), {'num': 0})['num']


def fmt_item(item, color=True):
    color = {
        events.STATUS_TODO: 'blue',
        events.STATUS_PROGRESS: 'yellow',
        events.STATUS_DONE: 'green',
        events.STATUS_BLOCKED: 'red',
        events.STATUS_DELETED: 'normal',
    }.get(item['status'])

    return '[gray #{}] [{} {}] [white {}]'.format(
        item['num'], color, item['status'], escape(item['text']))


def iter_backlog(items):
    return chain(
        iter_status(items, events.STATUS_PROGRESS),
        iter_status(items, events.STATUS_TODO),
    )


def iter_standup(done_gte, done_lt, items):
    return chain(
        (item for item in iter_status(items, events.STATUS_DONE)
         if done_gte <= item['done_at'] < done_lt),
        iter_status(items, events.STATUS_BLOCKED),
        iter_status(items, events.STATUS_PROGRESS),
        iter_status(items, events.STATUS_TODO),
    )


def iter_all(items):
    return chain(
        iter_backlog(items),
        iter_status(items, events.STATUS_BLOCKED),
        iter_status(items, events.STATUS_DONE),
        iter_status(items, events.STATUS_DELETED),
    )


def iter_status(items, status):
    return (item for item in items if item['status'] == status)

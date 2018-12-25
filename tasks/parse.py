from datetime import timedelta
from functools import partial

from datadispatch import datadispatch

from . import commands, events, model


def parse_input(state, input_, time):
    parts = input_.split(' ', 1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ''
    return _parse(state, cmd, args, time)


@datadispatch(lambda args, _: args[1])
def _parse(state, cmd, args, time):
    return [commands.println('unknown command, try "help"')]


@_parse.register('intro')
def _parse_intro(state, _, args, time):
    return [commands.println([
        'tasks is a simple interactive task queue that enables a kanban-like',
        'workflow. One item is always selected (its number being displayed ',
        'at the prompt) and marks the current item you are looking at; use ',
        'the commands to interact with the item. Most commands will also ',
        'support a number argument so that you can manipulate the other ',
        'items whithout having them selected, but generally the idea is to ',
        'work on one item at a time.',
    ])]


@_parse.register('help')
def _parse_help(state, _, args, time):
    return [commands.println([
        '  [white intro]',
        '     get a quick introduction to task\'s concepts',
        '  [white add TEXT]',
        '     add a new item in todo state',
        '     use addp/addd to add an item in progress/done status',
        '     use addt to add an item on top of the backlog',
        '  [white edit] [gray [[NUM]]]',
        '     edit current item/NUM',
        '  [white status]',
        '      display current item',
        '  [white backlog]',
        '      show in-progress and todo items',
        '  [white all]',
        '      show all items',
        '  [white standup] [gray [[DAYS]]]',
        '      show items suitable for daily standup',
        '  [white start] [gray [[NUM]]]',
        '      start progress on current item/NUM',
        '  [white done] [gray [[NUM]]]',
        '      mark current item/NUM done',
        '  [white blocked] [gray [[NUM]]]',
        '      mark current item/NUM as blocked',
        '  [white delete] [gray [[NUM]]]',
        '      mark current item/NUM as deleted',
        '  [white todo] [gray [[NUM]]]',
        '      mark current/NUM as todo',
        '  [white order]',
        '      re-order todo items',
        '  [white undo]',
        '      undo last command',
    ])]


@_parse.register('a')
@_parse.register('add')
@_parse.register('addd')
@_parse.register('addp')
@_parse.register('addt')
def _parse_add(state, cmd, args, time):
    event = events.item_added(
        1 + state['last_num'], args, on_top=cmd == 'addt')
    status = {
        'addd': events.STATUS_DONE,
        'addp': events.STATUS_PROGRESS,
    }.get(cmd, events.STATUS_TODO)
    item = {**event['item'], 'status': status}

    extra = [commands.store(events.item_status_changed(
        item['num'], status))] if cmd in ('addd', 'addp') else []

    return [
        commands.println('added {}'.format(model.fmt_item(item))),
        commands.store(event),
        *extra,
    ]


@_parse.register('st')
@_parse.register('status')
def _parse_status(state, _, args, time):
    if not state['selected']:
        return [commands.println('no item selected')]

    return [commands.println('currently on {}'.format(
        model.fmt_item(model.find(state['items'], state['selected']))))]


@_parse.register('bl')
@_parse.register('backlog')
def _parse_backlog(state, _, args, time):
    return _list(state, model.iter_backlog)


@_parse.register('all')
def _parse_all(state, _, args, time):
    return _list(state, model.iter_all)


@_parse.register('standup')
def _parse_standup(state, _, args, time):
    interval = timedelta(days=_parse_num(args, 1)).total_seconds()
    return _list(state, partial(model.iter_standup, time - interval, time))


def _list(state, iterator):
    items = list(iterator(state['items']))
    if not items:
        return []

    max_len = max(_item_len(state, item) for item in items)

    return [
        commands.println('{}{}{}'.format(
            ' ' * (max_len - _item_len(state, item)),
            '*' if item['num'] == state['selected'] else '',
            model.fmt_item(item)))
        for item in reversed(items)
    ]


def _item_len(state, item):
    return len(str(item['num'])) + int(item['num'] == state['selected'])


@_parse.register('order')
def _parse_order(state, _, args, time):
    items = list(model.iter_status(state['items'], events.STATUS_TODO))
    if len(items) < 2:
        return [commands.println('less than two todo items cannot be ordered')]

    content = ''.join(
        '#{} {}\n'.format(item['num'], item['text']) for item in items)

    return [commands.editor(content, events.item_order_edited)]


@_parse.register('undo')
def _parse_undo(state, _, args, time):
    if state['prev']:
        return [commands.store(events.undone())]

    return [commands.println('nothing to undo')]


@_parse.register('edit')
def _parse_edit(state, _, args, time):
    item, cmds = _get_item(state, args)
    if not item:
        return cmds

    content = item['text'] + '\n'
    num = item['num']

    return [commands.editor(content, partial(events.item_edit_requested, num))]


@_parse.register('s')
@_parse.register('start')
@_parse.register('d')
@_parse.register('done')
@_parse.register('x')
@_parse.register('delete')
@_parse.register('blocked')
@_parse.register('todo')
def _parse_status_change(state, cmd, args, time):
    item, cmds = _get_item(state, args)
    if not item:
        return cmds

    status = {
        's': events.STATUS_PROGRESS,
        'start': events.STATUS_PROGRESS,
        'd': events.STATUS_DONE,
        'done': events.STATUS_DONE,
        'x': events.STATUS_DELETED,
        'delete': events.STATUS_DELETED,
        'blocked': events.STATUS_BLOCKED,
        'todo': events.STATUS_TODO,
    }.get(cmd)

    return [commands.store(events.item_status_changed(item['num'], status))]


def _get_item(state, args):
    num = _parse_num(args)
    if args and not num:
        return None, [commands.println('bad item num')]

    if not num and not state['selected']:
        return None, [commands.println('no item selected')]

    item = model.find(state['items'], num or state['selected'])
    if not item:
        return None, [commands.println('bad item')]

    return item, []


def _parse_num(s, default=None):
    try:
        return int(s)
    except ValueError:
        return default

import json
from itertools import chain
from math import ceil, log

IN_PROGRESS = 'in-progress'
TODO = 'todo'
DONE = 'done'


def iter_status(tasks, status):
    return (task for task in tasks if task['status'] == status)


def iter_backlog(tasks):
    return chain(
        iter_status(tasks, IN_PROGRESS),
        iter_status(tasks, TODO)
    )


def iter_all(tasks):
    return chain(
        iter_backlog(tasks),
        iter_status(tasks, DONE)
    )


def find(tasks, num):
    try:
        return next(task for task in tasks if task['num'] == num)
    except StopIteration:
        return None


def greatest_num(tasks):
    greatest = 0

    if tasks:
        greatest = max(task['num'] for task in tasks)

    return greatest


def next_backlog_num(tasks):
    try:
        return next(iter_backlog(tasks))['num']
    except StopIteration:
        return None


def load(file_name):
    try:
        return json.load(open(file_name))
    except IOError:
        return []


def dump(file_name, tasks):
    if tasks:
        json.dump(tasks, open(file_name, 'w'), sort_keys=True, indent=2)


def shell_color(color, text):
    code = {
        'blue': '1;34',
        'yellow': '1;33',
        'green': '1;32',
        'white': '0;37',
        'gray': '1;30',
    }.get(color)

    return '\033[{code}m{text}\033[0m'.format(code=code, text=text)


def render(task, mark=None, colorizer=shell_color, digits=1):
    color = {
        'todo': 'blue',
        'in-progress': 'yellow',
        'done': 'green',
    }.get(task['status'], 'gray')

    if mark is None:
        symbol = ''
    elif mark:
        symbol = '*'
    else:
        symbol = ' '

    padding = ' ' * max(0, digits - len(str(task['num'])) - len(symbol))

    return ' '.join((
        colorizer('gray', '{padding}{symbol}#{num}'),
        colorizer(color, '{status}'),
    ) + (('{completed:.10}', ) if task['status'] == DONE else tuple()) + (
        colorizer('white', '{title}'),
    )).format(padding=padding, symbol=symbol, color=color, **task)


def render_list(tasks, selected, colorizer=shell_color):
    tasks = list(tasks)
    pad = int(ceil(log(max(1, greatest_num(tasks)))))
    return '\n'.join(
        render(task, task['num'] == selected, colorizer, pad) for task in tasks
    )

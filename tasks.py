import json
from itertools import chain

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


def next_num(tasks):
    greatest = 0

    if tasks:
        greatest = max(task['num'] for task in tasks)

    return greatest + 1


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

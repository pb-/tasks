from .tasks import next_backlog_num

CREATE = 1
START = 2
STOP = 3
COMPLETE = 4
SELECT = 5
ORDER = 6


def select(num):
    return dict(type=SELECT, num=num)


def select_next(tasks):
    return select(next_backlog_num(tasks))


def create(tasks, title, dt):
    greatest = 0

    if tasks:
        greatest = max(task['num'] for task in tasks)

    return dict(type=CREATE, num=greatest + 1, title=title, created=dt)


def start(num, dt):
    return dict(type=START, num=num, started=dt)


def stop(num):
    return dict(type=STOP, num=num)


def complete(num, dt):
    return dict(type=COMPLETE, num=num, completed=dt)


def order(order):
    return dict(type=ORDER, order=order)

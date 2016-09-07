from .tasks import next_backlog_num

CREATE = 1
START = 2
STOP = 3
COMPLETE = 4
SELECT = 5
ORDER = 6
BUMP = 7


def select(num):
    return dict(type=SELECT, num=num)


def bump(num):
    return dict(type=BUMP, num=num)


def select_next(tasks):
    return select(next_backlog_num(tasks))


def create(num, title, dt):
    return dict(type=CREATE, num=num, title=title, created=dt)


def start(num, dt):
    return dict(type=START, num=num, started=dt), bump(num)


def stop(num):
    return dict(type=STOP, num=num), bump(num)


def complete(num, dt):
    return dict(type=COMPLETE, num=num, completed=dt), bump(num)


def order(order):
    return dict(type=ORDER, order=order)

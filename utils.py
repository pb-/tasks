import os
from contextlib import contextmanager
from datetime import datetime
from errno import EACCES, EAGAIN
from fcntl import LOCK_EX, LOCK_NB, LOCK_UN, flock


class Locked(Exception):
    pass


def now():
    return datetime.now().isoformat()


@contextmanager
def lock(file_name):
    lock_name = '{}.lock'.format(file_name)
    try:
        with open(lock_name, 'w') as f:
            flock(f, LOCK_EX | LOCK_NB)
            try:
                yield
                flock(f, LOCK_UN)
            finally:
                os.remove(lock_name)
    except IOError as e:
        if e.errno in (EAGAIN, EACCES):
            raise Locked
        else:
            raise


def separate(predicate, list_):
    where_true = [x for x in list_ if predicate(x)]
    where_false = [x for x in list_ if not predicate(x)]
    return where_true + where_false

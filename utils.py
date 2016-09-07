import socket
from datetime import datetime


def now():
    return datetime.now().isoformat()


def get_lock():
    s = socket.socket()
    try:
        s.bind(('0.0.0.0', 9090))
        return s
    except socket.error:
        return None


def separate(predicate, list_):
    where_true = [x for x in list_ if predicate(x)]
    where_false = [x for x in list_ if not predicate(x)]
    return where_true + where_false

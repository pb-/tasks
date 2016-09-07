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

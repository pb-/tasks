INPUT_READ = 'input-read'
INITIALIZED = 'initialized'

ITEM_ADDED = 'item-added'
ITEM_STARTED = 'item-started'
ITEM_DONE = 'item-done'
ITEM_BLOCKED = 'item-blocked'
ITEM_DELETED = 'item-deleted'

STATUS_TODO = 'todo'
STATUS_PROGRESS = 'progress'
STATUS_BLOCKED = 'blocked'
STATUS_DONE = 'done'
STATUS_DELETED = 'deleted'


def input_read(input_):
    return {
        'type': INPUT_READ,
        'input': input_,
    }


def initialized():
    return {
        'type': INITIALIZED,
    }


def item_added(num, text, status=STATUS_TODO):
    return {
        'type': ITEM_ADDED,
        'item': {
            'num': num,
            'text': text,
            'status': status,
        },
    }


def item_started(num):
    return {
        'type': ITEM_STARTED,
        'num': num,
    }


def item_done(num):
    return {
        'type': ITEM_DONE,
        'num': num,
    }


def item_blocked(num):
    return {
        'type': ITEM_BLOCKED,
        'num': num,
    }


def item_deleted(num):
    return {
        'type': ITEM_DELETED,
        'num': num,
    }

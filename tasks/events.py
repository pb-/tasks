INPUT_READ = 'input-read'
INITIALIZED = 'initialized'

ITEM_ADDED = 'item-added'
ITEM_STATUS_CHANGED = 'item-status-changed'

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


def item_status_changed(num, status):
    return {
        'type': ITEM_STATUS_CHANGED,
        'num': num,
        'status': status,
    }

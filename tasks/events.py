INPUT_READ = 'input-read'
INITIALIZED = 'initialized'

ITEM_ADDED = 'item-added'

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


def item_added(num, text, status=STATUS_TODO):
    return {
        'type': ITEM_ADDED,
        'item': {
            'num': num,
            'text': text,
            'status': status,
        },
    }


def initialized():
    return {
        'type': INITIALIZED,
    }

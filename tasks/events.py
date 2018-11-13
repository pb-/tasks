INPUT_READ = 'input-read'
INITIALIZED = 'initialized'

ITEM_ADDED = 'item-added'
ITEM_STATUS_CHANGED = 'item-status-changed'
ITEM_ORDER_EDITED = 'item-order-edited'
ITEMS_REORDERED = 'items-reordered'
ITEM_EDIT_REQUESTED = 'item-edit-requested'
ITEM_EDITED = 'item-edited'
UNDONE = 'undone'

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


def item_order_edited(content):
    return {
        'type': ITEM_ORDER_EDITED,
        'content': content,
    }


def items_reordered(nums):
    return {
        'type': ITEMS_REORDERED,
        'nums': nums,
    }


def item_edit_requested(num, text):
    return {
        'type': ITEM_EDIT_REQUESTED,
        'num': num,
        'text': text,
    }


def item_edited(num, text):
    return {
        'type': ITEM_EDITED,
        'num': num,
        'text': text,
    }


def undone():
    return {
        'type': UNDONE,
    }

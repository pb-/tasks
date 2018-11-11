INPUT_READ = 'input-read'
INITIALIZED = 'initialized'

ITEM_ADDED = 'item-added'


def input_read(input_):
    return {
        'type': INPUT_READ,
        'input': input_,
    }


def item_added(num, text):
    return {
        'type': ITEM_ADDED,
        'num': num,
        'text': text,
    }


def initialized():
    return {
        'type': INITIALIZED,
    }

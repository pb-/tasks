QUIT = 'quit'
PRINTLN = 'println'
STORE = 'store'
EDITOR = 'editor'

def println(text):
    return {
        'type': PRINTLN,
        'lines': [text] if isinstance(text, str) else text
    }


def quit(error=None):
    return {
        'type': QUIT,
        'error': error,
    }


def store(event):
    return {
        'type': STORE,
        'event': event,
    }

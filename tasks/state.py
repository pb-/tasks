from . import commands, events
from .func import valuedispatch


def initial_state():
    return {
        'items': [],
        'selected': 0,
        'last_num': 0,
    }


def render(state):
    if state['selected']:
        return '#{} >'.format(state['selected'])
    else:
        return '>'


@valuedispatch(lambda args, _: args[1].get('type'))
def update(state, event, time):
    raise ValueError('bad event: {}'.format(event.get('type')))


@update.register(events.INITIALIZED)
def _update_initialized(state, event, time):
    return state, [commands.println([
        'Welcome to tasks',
        'type help for help, exit with ^D or ^C',
    ])]


@update.register(events.INPUT_READ)
def _update_input(state, event, time):
    parts = event['input'].split(' ')
    if parts[0] == 'add' and len(parts) > 1:
        return state, [
            commands.println('added {}'.format(parts[1])),
            commands.store(events.item_added(1 + state['last_num'], parts[1])),
        ]


    return state, []


@update.register(events.ITEM_ADDED)
def _update_item_added(state, event, time):
    return {
        **state,
        'items': [*state['items'], {
            'num': event['num'],
            'text': event['text'],
        }],
        'last_num': event['num']
    }, []

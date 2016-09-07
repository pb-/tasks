from . import actions
from .tasks import DONE, IN_PROGRESS, TODO


def selected(state, action):
    if action['type'] == actions.SELECT:
        return action['num']
    else:
        return state


def task(state, action):
    if state['num'] == action['num']:
        if action['type'] == actions.START:
            update = [
                ('status', IN_PROGRESS),
                ('started', action['started']),
            ]
        elif action['type'] == actions.COMPLETE:
            update = [
                ('status', DONE),
                ('completed', action['completed']),
            ]
        elif action['type'] == actions.STOP:
            update = [
                ('status', TODO)
            ]
        else:
            update = []
        return dict(state.items() + update)
    else:
        return state


def tasks(state, action):
    if action['type'] == actions.CREATE:
        return state + [{
            'num': action['num'],
            'title': action['title'],
            'created': action['created'],
            'status': TODO,
        }]
    elif action['type'] == actions.ORDER:
        order = action['order']
        ordered = [t for num in order for t in state if t['num'] == num]
        rest = [t for t in state if t['num'] not in order]

        return ordered + rest
    else:
        return [task(t, action) for t in state]


def root(state, action):
    return dict(
        selected=selected(state['selected'], action),
        tasks=tasks(state['tasks'], action),
    )


def dispatch(state, action):
    if isinstance(action, dict):
        state = root(state, action)
    else:
        for subaction in action:
            state = dispatch(state, subaction)

    return state

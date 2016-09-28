import os
import re
from functools import partial

from . import actions, reducers, tasks, utils
from .parser import ParseError, option, parse, positional, remainder

_commands = []


class Undo(Exception):
    pass


def evaluate(input_, state):

    try:
        return parse(input_, _commands, state)
    except ParseError as e:
        print(e)
        return state


def register(*args, **kwargs):
    def wrapper(aliases, arguments, function):
        _commands.append({
            'name': function.__name__,
            'help': function.__doc__,
            'function': function,
            'aliases': aliases,
            'arguments': arguments,
        })
        return function

    if len(args) == 1 and callable(args[0]):
        wrapper([], [], args[0])
    else:
        return partial(wrapper, args, kwargs.get('arguments', []))


@register('a', arguments=(
    option('--start', '-s'),
    option('--done', '-d'),
    remainder('title'),
))
def add(args, state):
    """Add a new task."""
    num = tasks.greatest_num(state['tasks']) + 1
    action = actions.create(num, args['title'], utils.now())
    state = reducers.dispatch(state, action)
    if args['start']:
        state = reducers.dispatch(
            state, actions.start(action['num'], utils.now())
        )
        state = reducers.dispatch(state, actions.select(action['num']))
    if args['done']:
        state = reducers.dispatch(
            state, actions.complete(action['num'], utils.now())
        )

    print('Added ' + tasks.render(tasks.find(state['tasks'], num)))
    return state


@register(arguments=(
    positional('num', type_=int, required=False),
))
def start(args, state):
    """Start working on a task (mark as in-progress)."""
    state = reducers.dispatch(state, actions.start(
        args['num'] or state['selected'], utils.now()
    ))
    return state


@register('complete', arguments=(
    positional('num', type_=int, required=False),
))
def done(args, state):
    """Complete a task (mark as done)."""
    state = reducers.dispatch(state, actions.complete(
        args['num'] or state['selected'], utils.now()
    ))
    return state


@register('list')
def all(args, state):
    """List all tasks, including completed and deleted."""
    print(tasks.render_list(tasks.iter_all(state['tasks']), state['selected']))
    return state


@register
def standup(args, state):
    """List tasks in a format suitable for standup."""
    print(tasks.render_list(
        tasks.iter_standup(state['tasks']), state['selected'])
    )
    return state


@register('bl')
def backlog(args, state):
    """List todo and in-progress tasks."""
    print(tasks.render_list(tasks.iter_backlog(
        state['tasks']), state['selected']
    ))
    return state


@register
def status(args, state):
    """Show the currently selected task."""
    task = tasks.find(state['tasks'], state['selected'])
    if task:
        print('Currently selected ' + tasks.render(task, mark=None))
    else:
        print('No task selected')

    return state


# overwrites builtin help, but that should be ok
@register(arguments=(
    positional('command', required=False),
))
def help(args, state):
    """Get help."""

    if args['command']:
        try:
            cmd = next(c for c in _commands if c['name'] == args['command'])
            print('  {}'.format(cmd['name']))
            pass
        except StopIteration:
            print('No such command')
    else:
        print('')
        for command in _commands:
            print('  {name:10} {help}'.format(**command))
        print('')
        print('Type help COMMAND for detailed help')
    return state


@register
def order(args, state):
    """Re-order todo items in an external editor."""
    path = os.path.join('/tmp', 'tasks.{}.edit'.format(os.getpid()))
    open(path, 'w').write(tasks.render_list(
        tasks.iter_backlog(state['tasks']), None, lambda _, text: text))
    os.system('editor {}'.format(path))

    order = []
    pattern = re.compile(r'^ *#(?P<num>\d+) ')
    with open(path) as f:
        for line in f:
            match = pattern.match(line)
            if match:
                order.append(int(match.group('num')))

    os.remove(path)

    return reducers.dispatch(state, actions.order(order))


@register(arguments=(
    positional('num', type_=int, required=False),
))
def edit(args, state):
    """Change the title of an item."""
    task = tasks.find(state['tasks'], args['num'] or state['selected'])
    path = os.path.join('/tmp', 'tasks.{}.edit'.format(os.getpid()))

    open(path, 'w').write(task['title'])
    os.system('editor {}'.format(path))
    title = open(path).read().strip()

    os.remove(path)

    return reducers.dispatch(state, actions.edit(
        args['num'] or state['selected'], title))


@register
def clear(args, state):
    """Clear screen."""
    os.system('clear')
    return state


@register(arguments=(
    positional('num', type_=int, required=False),
))
def delete(args, state):
    """Delete a task (mark as deleted)."""
    state = reducers.dispatch(state, actions.delete(
        args['num'] or state['selected'], utils.now()
    ))
    return state


@register
def undo(args, state):
    """Undo last command."""
    raise Undo

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


def register(name, help_=None, aliases=[], arguments=[]):
    def wrapper(name, help_, aliases, arguments, function):
        _commands.append({
            'name': name,
            'help': help_,
            'function': function,
            'aliases': aliases,
            'arguments': arguments,
        })
        return function
    return partial(wrapper, name, help_, aliases, arguments)


@register('add', help_='add a new task', aliases=['a'], arguments=(
    option('--start', '-s'),
    option('--done', '-d'),
    remainder('title'),
))
def add(args, state):
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

    return state


@register('start', help_='start a task', arguments=(
    positional('num', type_=int, required=False),
))
def start(args, state):
    state = reducers.dispatch(state, actions.start(
        args['num'] or state['selected'], utils.now()
    ))
    return state


@register('done', help_='mark a task as completed', aliases=['complete'],
          arguments=(
    positional('num', type_=int, required=False),
))
def done(args, state):
    state = reducers.dispatch(state, actions.complete(
        args['num'] or state['selected'], utils.now()
    ))
    return state


@register('list', help_='list all tasks, including completed', aliases=['all'])
def all(args, state):
    print(tasks.render_list(tasks.iter_all(state['tasks']), state['selected']))
    return state


@register('standup', help_='list all tasks for standup')
def standup(args, state):
    print(tasks.render_list(
        tasks.iter_standup(state['tasks']), state['selected'])
    )
    return state


@register('backlog', help_='list todo and in-progress tasks', aliases=['bl'])
def backlog(args, state):
    print(tasks.render_list(tasks.iter_backlog(
        state['tasks']), state['selected']
    ))
    return state


@register('status', help_='show currently selected task')
def status(args, state):
    task = tasks.find(state['tasks'], state['selected'])
    if task:
        print('Currently selected ' + tasks.render(task, mark=None))
    else:
        print('No task selected')

    return state


@register('help', help_='show this help')
def help(args, state):
    for command in _commands:
        print('  {name:10} {help}'.format(**command))
    print('')
    print('Type help COMMAND for detailed help')
    return state


@register('order', help_='re-order todo items')
def order(args, state):
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


@register('edit', help_='change item title', arguments=(
    positional('num', type_=int, required=False),
))
def edit(args, state):
    task = tasks.find(state['tasks'], args['num'] or state['selected'])
    path = os.path.join('/tmp', 'tasks.{}.edit'.format(os.getpid()))

    open(path, 'w').write(task['title'])
    os.system('editor {}'.format(path))
    title = open(path).read().strip()

    os.remove(path)

    return reducers.dispatch(state, actions.edit(
        args['num'] or state['selected'], title))


@register('clear', help_='clear screen')
def clear(args, state):
    os.system('clear')
    return state


@register('delete', help_='delete a task', arguments=(
    positional('num', type_=int, required=False),
))
def delete(args, state):
    state = reducers.dispatch(state, actions.delete(
        args['num'] or state['selected'], utils.now()
    ))
    return state


@register('undo', help_='undo last command')
def undo(args, state):
    raise Undo

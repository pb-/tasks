import os
import re
from argparse import ArgumentParser
from functools import partial

from . import actions, reducers, tasks, utils


class ParseError(Exception):
    pass


class CommandParser(ArgumentParser):
    def error(self, message):
        raise ParseError(message)


_parser = CommandParser(prog='', add_help=False)
_subparsers = _parser.add_subparsers(dest='command')


def evaluate(input_, state):
    try:
        args = _parser.parse_args(input_.split(' '))
        return args.func(state, args)
    except ParseError as e:
        print(e)
        return state


# the word 'argument' has multiple meanings in this function, unfortunately
# (Python functon argument as in arg/kwarg and argument as in argument for the
# argument parser.)
def register(*aliases, **kwargs):
    def wrapper(aliases, kwargs, function):
        arguments = kwargs.pop('args') if 'args' in kwargs else []
        for command in aliases:
            parser = _subparsers.add_parser(command, **kwargs)
            for arg_args, arg_kwargs in arguments:
                parser.add_argument(*arg_args, **arg_kwargs)
            parser.set_defaults(func=function)
        return function
    return partial(wrapper, aliases, kwargs)


def arg(*args, **kwargs):
    return args, kwargs


@register('add', 'a', help='add a new task', args=(
    arg('title', nargs='+', metavar='TITLE'),
    arg('-s', '--start', action='store_true'),
))
def add(state, args):
    num = tasks.greatest_num(state['tasks']) + 1
    action = actions.create(num, ' '.join(args.title), utils.now())
    state = reducers.root(state, action)
    if args.start:
        state = reducers.root(state, actions.start(action['num'], utils.now()))
        state = reducers.root(state, actions.select(action['num']))

    return state


@register('start', help='start a task', args=(
    arg('num', nargs='?', type=int),
))
def start(state, args):
    state = reducers.root(state, actions.start(
        args.num or state['selected'], utils.now()
    ))
    return state


@register('done', 'complete', help='mark a task as completed', args=(
    arg('num', nargs='?', type=int),
))
def done(state, args):
    state = reducers.root(state, actions.complete(
        args.num or state['selected'], utils.now()
    ))
    return state


@register('list', 'all', help='list all tasks, including completed')
def all(state, args):
    print(tasks.render_list(tasks.iter_all(state['tasks']), state['selected']))
    return state


@register('backlog', 'bl', help='list todo and in-progress tasks')
def backlog(state, args):
    print(tasks.render_list(tasks.iter_backlog(
        state['tasks']), state['selected']
    ))
    return state


@register('status', help='show currently selected task')
def status(state, args):
    task = tasks.find(state['tasks'], state['selected'])
    if task:
        print('Currently selected ' + tasks.render(task))
    else:
        print('No task selected')

    return state


@register('help', help='show this help')
def help(state, args):
    _parser.print_help()
    return state


@register('order', help='re-order todo items')
def order(state, args):
    path = os.path.join('/tmp', 'tasks.{}.edit'.format(os.getpid()))
    open(path, 'w').write(tasks.render_list(
        tasks.iter_backlog(state['tasks']), None, lambda _, text: text))
    os.system('editor {}'.format(path))

    order = []
    pattern = re.compile(r'^ ?#(?P<num>\d+) ')
    with open(path) as f:
        for line in f:
            match = pattern.match(line)
            if match:
                order.append(int(match.group('num')))

    os.remove(path)

    return reducers.root(state, actions.order(order))


@register('clear', help='clear screen')
def clear(state, args):
    os.system('clear')
    return state

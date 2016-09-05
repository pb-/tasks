import os
import readline
from argparse import ArgumentParser
from datetime import datetime

from . import actions, reducers, tasks

tasks_file = os.path.join(os.getenv('HOME'), '.tasks.json')

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')


class ParseError(Exception):
    pass


class CommandParser(ArgumentParser):
    def error(self, message):
        raise ParseError(message)


def create_parser():
    parser = CommandParser()
    subparsers = parser.add_subparsers(dest='command')

    add = subparsers.add_parser('add')
    add.add_argument('title', nargs='+', metavar='TITLE')
    add.add_argument('--start', '-s', action='store_true')

    subparsers.add_parser('all')
    subparsers.add_parser('backlog')
    subparsers.add_parser('status')

    start = subparsers.add_parser('start')
    start.add_argument('num', nargs='?', type=int)

    done = subparsers.add_parser('done')
    done.add_argument('num', nargs='?', type=int)

    return parser


def prompt(state):
    return '#{}> '.format(state['selected']) if state['selected'] else '> '


def render_task(task, mark=None):
    color = {
        'todo': 34,
        'in-progress': 33,
        'done': 32,
    }.get(task['status'], 30)

    if mark is None:
        symbol = ''
    elif mark:
        symbol = '*'
    else:
        symbol = ' '

    return (
        '\033[1;30m{symbol}#{num}\033[0m '
        '\033[1;{color}m{status}\033[0m '
        '\033[0;37m{title}\033[0m'
    ).format(symbol=symbol, color=color, **task)


def render_task_list(tasks, selected):
    for task in tasks:
        print(render_task(task, task['num'] == selected))


def run():
    parser = create_parser()
    state = dict(selected=None, tasks=tasks.load(tasks_file))
    state = reducers.root(state, actions.select_next(state['tasks']))
    while True:
        try:
            args = parser.parse_args(raw_input(prompt(state)).split(' '))
            now = datetime.now().isoformat()

            if args.command == 'all':
                render_task_list(
                    tasks.iter_all(state['tasks']), state['selected'])
            elif args.command == 'backlog':
                render_task_list(
                    tasks.iter_backlog(state['tasks']), state['selected'])
            elif args.command == 'status':
                task = tasks.find(state['tasks'], state['selected'])
                if task:
                    print('Currently selected ' + render_task(task))
                else:
                    print('No task selected')
            elif args.command == 'add':
                action = actions.create(
                    state['tasks'], ' '.join(args.title), now
                )
                state = reducers.root(state, action)
                if args.start:
                    state = reducers.root(state, actions.start(
                        action['num'], now))
                    state = reducers.root(state, actions.select(action['num']))

            elif args.command == 'start':
                state = reducers.root(state, actions.start(
                    args.num or state['selected'], now
                ))
            elif args.command == 'done':
                state = reducers.root(state, actions.complete(
                    args.num or state['selected'], now
                ))
                state = reducers.root(state, actions.select_next(
                    state['tasks']
                ))

        except ParseError as e:
            print(e)
        except EOFError:
            print('')
            break

    tasks.dump(tasks_file, state['tasks'])


if __name__ == '__main__':
    run()

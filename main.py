import os
import readline

from textwrap import dedent

from . import actions, commands, reducers, tasks


def configure_readline():
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')


def prompt(state):
    return '#{}> '.format(state['selected']) if state['selected'] else '> '


def print_banner():
    print(dedent("""\
        welcome to tasks
        type help for help, exit with ^D or with ^C to discard changes
    """))


def run():
    print_banner()
    tasks_file = os.path.join(os.getenv('HOME'), '.tasks.json')
    state = dict(selected=None, tasks=tasks.load(tasks_file))

    configure_readline()

    while True:
        selected = tasks.find(state['tasks'], state['selected'])
        if not selected or selected['status'] != tasks.IN_PROGRESS:
            state = reducers.root(state, actions.select_next(state['tasks']))
        try:
            input_ = raw_input(prompt(state))
            state = commands.evaluate(input_, state)
            if state is None:
                raise Exception('command returned None state')
        except EOFError:
            print('')
            break

    tasks.dump(tasks_file, state['tasks'])


if __name__ == '__main__':
    run()

import os
import readline

from . import actions, commands, reducers, tasks

tasks_file = os.path.join(os.getenv('HOME'), '.tasks.json')

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')


def prompt(state):
    return '#{}> '.format(state['selected']) if state['selected'] else '> '


def run():
    state = dict(selected=None, tasks=tasks.load(tasks_file))
    while True:
        if state['selected'] is None:
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

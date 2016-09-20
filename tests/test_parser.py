from unittest import TestCase

from mock import MagicMock

from ..parser import (ParseError, _parse_args, option, parse, positional,
                      remainder)


class ParserTest(TestCase):
    def test_parse_args(self):
        syntax = [
            option('--debug', '-d'),
            option('--verbose', '-v'),
            positional('a'),
            positional('b'),
            positional('c', required=False, default='x'),
            remainder('rest'),
        ]

        line = '   z  -v -d 20 10 foo  bar'
        parsed = _parse_args(line.split(' '), syntax)
        self.assertEqual(parsed, {
            'debug': True,
            'verbose': True,
            'a': 'z',
            'b': '20',
            'c': '10',
            'rest': 'foo  bar',
        })

        line = ' --debug z 20 --  foo bar --verbose'
        parsed = _parse_args(line.split(' '), syntax)
        self.assertEqual(parsed, {
            'debug': True,
            'verbose': False,
            'a': 'z',
            'b': '20',
            'c': 'x',
            'rest': ' foo bar --verbose',
        })

        with self.assertRaises(ParseError):
            line = '--debug z -- foo bar --verbose'
            _parse_args(line.split(' '), syntax)

    def test_parse(self):
        add_fn = MagicMock()
        done_fn = MagicMock()

        commands = [{
            'name': 'add',
            'function': add_fn,
            'aliases': ('a', 'new'),
            'arguments': [
                option('--start', '-s'),
                remainder('title'),
            ],
        }, {
            'name': 'done',
            'function': done_fn,
            'arguments': [
                positional('num', type_=int, required=False),
            ],
        }]

        with self.assertRaises(ParseError):
            parse('exit', commands)

        parse('add --start the quick brown fox...', commands)
        add_fn.assert_called_with({
            'start': True,
            'title': 'the quick brown fox...',
        })

        parse('add bla', commands)
        add_fn.assert_called_with({
            'start': False,
            'title': 'bla',
        })

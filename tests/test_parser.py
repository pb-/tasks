from unittest import TestCase

from mock import MagicMock

from ..parser import (ParseError, _parse_args, option, parse, positional,
                      remainder)


class ParserTest(TestCase):
    def test_option(self):
        opt = option('--debug', '-d')

        unparsed = 'foo bar -d baz'.split(' ')
        parsed, unparsed_after, noparse = opt([], unparsed, [])
        self.assertEqual(parsed, [('debug', True)])
        self.assertEqual(unparsed_after, ['foo', 'bar', 'baz'])
        self.assertFalse(noparse)

        unparsed = 'foo --debug'.split(' ')
        parsed, unparsed_after, noparse = opt([], unparsed, [])
        self.assertEqual(parsed, [('debug', True)])
        self.assertEqual(unparsed_after, ['foo'])
        self.assertFalse(noparse)

        unparsed = 'bar 0'.split(' ')
        parsed, unparsed_after, noparse = opt([], unparsed, [])
        self.assertEqual(parsed, [('debug', False)])
        self.assertEqual(unparsed_after, ['bar', '0'])
        self.assertFalse(noparse)

    def test_positional(self):
        pos = positional('n')

        with self.assertRaises(ParseError):
            # required argument not given
            pos([], [], [])

        unparsed = ['10', '20']
        parsed, unparsed_after, noparse = pos([], unparsed, [])
        self.assertEqual(parsed, [('n', '10')])
        self.assertEqual(unparsed_after, ['20'])
        self.assertFalse(noparse)

        pos = positional('n', type_=int)
        with self.assertRaises(ParseError):
            # type error
            pos([], ['x'], [])

        unparsed = ['10']
        parsed, unparsed_after, noparse = pos([], unparsed, [])
        self.assertEqual(parsed, [('n', 10)])
        self.assertFalse(unparsed_after)
        self.assertFalse(noparse)

        pos = positional('n', required=False, default='def')
        parsed, unparsed_after, noparse = pos([], [], [])
        self.assertEqual(parsed, [('n', 'def')])
        self.assertFalse(unparsed_after)
        self.assertFalse(noparse)

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

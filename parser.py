from functools import partial


class ParseError(Exception):
    pass


def syntax_element(function):
    def f(func, *args, **kwargs):
        return partial(func, *args, **kwargs)
    return partial(f, function)


@syntax_element
def option(long_name, short_name, parsed, unparsed, noparse):
    name = long_name[2:]
    try:
        index = next(
            i for i, arg in enumerate(unparsed)
            if arg in (short_name, long_name)
        )
        return parsed + [(name, True)], \
            unparsed[:index] + unparsed[index+1:], noparse
    except StopIteration:
        return parsed + [(name, False)], unparsed, noparse


@syntax_element
def remainder(name, parsed, unparsed, noparse):
    return parsed + [(name, ' '.join(unparsed + noparse))], [], []


@syntax_element
def positional(name, parsed, unparsed, noparse,
               type_=str, default=None, required=True):
    if required and default:
        raise ParseError('Argument {} is required and has default'.format(
            name))

    while unparsed and not unparsed[0]:
        unparsed = unparsed[1:]

    if unparsed:
        try:
            value = type_(unparsed[0])
        except Exception:
            raise ParseError('Bad value for argument {} of {}'.format(
                name, type_))

        return parsed + [(name, value)], unparsed[1:], noparse
    else:
        if required:
            raise ParseError('Required argument {} not provided'.format(name))
        else:
            return parsed + [(name, default)], [], noparse


def _split_args(args):
    try:
        index = next(i for i, arg in enumerate(args) if arg == '--')
        return args[:index], args[index+1:]
    except StopIteration:
        return args, []


def _parse_args(args, syntax):
    parsed = []
    unparsed, noparse = _split_args(args)

    for token in syntax:
        parsed, unparsed, noparse = token(parsed, unparsed, noparse)

    if unparsed or noparse:
        raise ParseError('Extra arguments: {}'.format(
            ' '.join(unparsed + noparse)))

    return dict(parsed)


def parse(line, commands, *args, **kwargs):
    # what about empty line
    parts = line.split(' ')

    try:
        command = next(
            c for c in commands
            if c['name'] == parts[0] or parts[0] in c.get('aliases', []))
        cmd_args = _parse_args(parts[1:], command['arguments'])
        return command['function'](cmd_args, *args, **kwargs)
    except StopIteration:
        raise ParseError('No such command: {}'.format(parts[0]))

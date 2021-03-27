import re

_RE = re.compile('([^[\\]\\\\]+|\\[|\\]|\\\\)')
_MAP = {
    'blue': '1;34',
    'cyan': '1;36',
    'gray': '1;30',
    'green': '1;32',
    'normal': '0',
    'red': '1;31',
    'white': '0;37',
    'yellow': '1;33',
}


def shell_color(text):
    return _format(text, True)


def no_color(text):
    return _format(text, False)


def escape(text):
    return text.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')


def _format(text, with_color):
    return ''.join(t for t in _format_tokens(_tokenize(text), with_color))


def _tokenize(text):
    return (m.group(0) for m in _RE.finditer(text))


def _format_tokens(tokens, with_color):
    while True:
        try:
            token = next(tokens)
        except StopIteration:
            return ''

        if token == '\\':
            yield _format_escape(tokens)
        elif token == '[':
            yield _format_open_bracket(tokens, with_color)
        elif token == ']':
            yield _format_close_bracket(with_color)
        else:
            yield token


def _format_escape(tokens):
    token = next(tokens)

    if token in ('\\', '[', ']'):
        return token

    raise ParseException(f"unsupported escape sequence: '{token}'")


def _format_open_bracket(tokens, with_color):
    try:
        color, text = next(tokens).split(' ', maxsplit=1)
    except ValueError:
        raise ParseException("empty color directive")

    if color not in _MAP:
        raise ParseException(f"unsupported color: '{color}'")

    if with_color:
        return f'\033[{_MAP[color]}m{text}'

    return text


def _format_close_bracket(with_color):
    if with_color:
        return '\033[0m'

    return ''


class ParseException(Exception):
    pass

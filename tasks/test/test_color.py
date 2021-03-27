from ..color import ParseException, escape, no_color, shell_color


def assert_parse_error(func, message):
    try:
        func()
        assert False, message
    except ParseException:
        return


assert escape('hello') == 'hello'
assert escape('hello [world]') == 'hello \\[world\\]'
assert escape(escape('hello [world]')) == 'hello \\\\\\[world\\\\\\]'

assert no_color('hello world') == 'hello world'
assert no_color('\\[hello \\\\ world\\]') == '[hello \\ world]'
assert no_color('this is [green green]') == 'this is green'

assert shell_color('this is [green green]') == 'this is \033[1;32mgreen\033[0m'

assert shell_color(escape('[red not red]')) == '[red not red]'

assert_parse_error(
    lambda: shell_color('\\invalid'), 'expected escape exception')
assert_parse_error(lambda: shell_color('\\0'), 'expected escape exception')
assert_parse_error(
    lambda: shell_color('[purple colored]'), 'expected escape exception')
assert_parse_error(lambda: shell_color('[['), 'expected escape exception')

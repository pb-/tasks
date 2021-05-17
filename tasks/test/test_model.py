from ..events import STATUS_PROGRESS, STATUS_TODO
from ..model import fmt_item

_multiline_text = """buy tomatoes
1kg should be enough
Reference: https://en.wikipedia.org/wiki/Tomato
"""


def test_format():
    item1 = {"num": 1, "text": "buy milk", "status": STATUS_TODO}
    item2 = {"num": 2, "text": _multiline_text, "status": STATUS_PROGRESS}

    assert fmt_item(item1) == "[gray #1] [blue todo] [white buy milk]"
    assert (
        fmt_item(item1, shortcut="a")
        == "[gray #1] ([cyan a]) [blue todo] [white buy milk]"
    )
    assert (
        fmt_item(item2)
        == "[gray #2] [yellow progress] [white buy tomatoes (…)]"
    )

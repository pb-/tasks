from ..update import _prune_prev


def test_undo_prune():
    s1 = {'stuff': 1, 'prev': None}
    assert not _prune_prev(s1, 0)

    assert _prune_prev(s1, 1) == s1
    assert _prune_prev(s1, 5) == s1

    s2 = {
        'stuff': 1,
        'prev': {
            'stuff': 2,
            'prev': None,
        }
    }
    assert _prune_prev(s2, 2) == s2
    assert _prune_prev(s2, 1) == s1

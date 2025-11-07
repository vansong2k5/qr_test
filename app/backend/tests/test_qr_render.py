from src.qr.render import _is_finder_module


def test_is_finder_module():
    size = 29
    assert _is_finder_module(0, 0, size)
    assert _is_finder_module(6, 6, size)
    assert _is_finder_module(size - 1, 6, size)
    assert not _is_finder_module(10, 10, size)

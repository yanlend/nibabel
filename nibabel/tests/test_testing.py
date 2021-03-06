""" Test testing utilities
"""

import sys

from warnings import warn, simplefilter

import numpy as np

from ..testing import catch_warn_reset, assert_allclose_safely

from nose.tools import assert_equal, assert_raises


def assert_warn_len_equal(mod, n_in_context):
    mod_warns = mod.__warningregistry__
    # Python 3.4 appears to clear any pre-existing warnings of the same type,
    # when raising warnings inside a catch_warnings block. So, there is a
    # warning generated by the tests within the context manager, but no
    # previous warnings.
    if 'version' in mod_warns:
        assert_equal(len(mod_warns), 2)  # including 'version'
    else:
        assert_equal(len(mod_warns), n_in_context)


def test_catch_warn_reset():
    # Initial state of module, no warnings
    my_mod = sys.modules[__name__]
    assert_equal(getattr(my_mod, '__warningregistry__', None), None)
    with catch_warn_reset(modules=[my_mod]):
        simplefilter('ignore')
        warn('Some warning')
    assert_equal(my_mod.__warningregistry__, {})
    # Without specified modules, don't clear warnings during context
    with catch_warn_reset():
        simplefilter('ignore')
        warn('Some warning')
    assert_warn_len_equal(my_mod, 1)
    # Confirm that specifying module keeps old warning, does not add new
    with catch_warn_reset(modules=[my_mod]):
        simplefilter('ignore')
        warn('Another warning')
    assert_warn_len_equal(my_mod, 1)
    # Another warning, no module spec does add to warnings dict, except on
    # Python 3.4 (see comments in `assert_warn_len_equal`)
    with catch_warn_reset():
        simplefilter('ignore')
        warn('Another warning')
    assert_warn_len_equal(my_mod, 2)


def test_assert_allclose_safely():
    # Test the safe version of allclose
    assert_allclose_safely([1, 1], [1, 1])
    assert_allclose_safely(1, 1)
    assert_allclose_safely(1, [1, 1])
    assert_allclose_safely([1, 1], 1 + 1e-6)
    assert_raises(AssertionError, assert_allclose_safely, [1, 1], 1 + 1e-4)
    # Broadcastable matrices
    a = np.ones((2, 3))
    b = np.ones((3, 2, 3))
    eps = np.finfo(np.float).eps
    a[0, 0] = 1 + eps
    assert_allclose_safely(a, b)
    a[0, 0] = 1 + 1.1e-5
    assert_raises(AssertionError, assert_allclose_safely, a, b)
    # Nans in same place
    a[0, 0] = np.nan
    b[:, 0, 0] = np.nan
    assert_allclose_safely(a, b)
    # Never equal with nans present, if not matching nans
    assert_raises(AssertionError,
                  assert_allclose_safely, a, b,
                  match_nans=False)
    b[0, 0, 0] = 1
    assert_raises(AssertionError, assert_allclose_safely, a, b)
    # Test allcloseness of inf, especially np.float128 infs
    for dtt in np.sctypes['float']:
        a = np.array([-np.inf, 1, np.inf], dtype=dtt)
        b = np.array([-np.inf, 1, np.inf], dtype=dtt)
        assert_allclose_safely(a, b)
        b[1] = 0
        assert_raises(AssertionError, assert_allclose_safely, a, b)
    # Empty compares equal to empty
    assert_allclose_safely([], [])

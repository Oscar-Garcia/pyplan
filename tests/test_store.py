# -*- coding: utf-8 -*-
import pytest

from ..pyplan.store import ChainScopeStore


def test_scopes():

    store = ChainScopeStore()

    assert store.init is not None

    col1 = store.create_scope(1)
    col2 = store.create_scope(2, 1)
    col3 = store.create_scope(3)

    col1.insert_record('a', True)
    col2.insert_record('b', True)

    assert col1.get_record('a')
    assert col2.get_record('a')
    with pytest.raises(KeyError):
        col1.get_record('b')
    with pytest.raises(KeyError):
        col3.get_record('b')

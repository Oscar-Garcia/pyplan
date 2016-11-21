# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
import pytest

from ..pyplan.builtins import Frame
from ..pyplan.graph import SearchSpace, Graph
from ..pyplan.solver import Solver
from ..pyplan.store import ChainScopeStore


@pytest.fixture
def frame():
    solver = Solver(Graph(), None)
    store = ChainScopeStore()
    search_space = SearchSpace()
    frame = Frame(solver, store, search_space)
    frame.selected = solver.domain.create_node()
    setattr(frame.selected, 'context_id', 0)
    return frame


def test_no_write(frame):
    bins = frame.ro_builtins
    assert 'sput' not in bins
    assert 'sput_all' not in bins


def test_sput(frame):
    bins = frame.w_builtins
    sput = bins['sput']
    sget = bins['sget']
    sput('hello', 'world')
    assert sget('hello') == 'world'


def test_sput_all(frame):
    bins = frame.w_builtins
    sput_all = bins['sput_all']
    sget = bins['sget']
    sput_all('hello', 'world')
    assert sget('hello') == 'world'
    assert frame.store.init.get_record('hello') == 'world'

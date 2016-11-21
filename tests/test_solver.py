# -*- coding: utf-8 -*-
from ..pyplan.solver import Solver
from ..pyplan.store import NoScopeStore
from ..pyplan.graph import Graph


def has_result(sget, **kwargs):  # pylint: disable=unused-argument
    return sget('result', None) is not None


def test_simple_solver():
    store = NoScopeStore()
    context = store.init
    domain = Graph()
    node = domain.node_builder

    # create the domain a simple if
    root = node()

    can_vote = node(
        in_nodes=root,
        test="sget('person')['age'] >= 18",
        action="sput('result', 'Can vote')"
    )
    assert getattr(can_vote, 'test', None)
    assert getattr(can_vote, 'action', None)

    can_not_vote = node(
        in_nodes=root,
        test="sget('person')['age'] < 18",
        action="sput('result', 'Can not vote')"
    )

    assert getattr(can_not_vote, 'test', None)
    assert getattr(can_not_vote, 'action', None)

    # create the problem
    context.insert_record('person', {'age': 15})

    # run the solver
    solver = Solver(domain=domain, solution_checker=has_result)
    solver.backtrack = False
    solver.eval(root, store=store)

    assert context.get_record('result') == 'Can not vote'

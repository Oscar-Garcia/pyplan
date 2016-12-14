# -*- coding: utf-8 -*-

from .graph import Graph, SearchSpace
from .nodes import Node


class PythonCodeError(Exception):
    def __init__(self, source_code):
        super().__init__()
        self.source_code = source_code

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.source_code)


def succesors_generation(node: Node, domain: Graph, **kwargs):  # pylint: disable=unused-argument
    return domain.successors(domain.get_node(node.reference))


def order_evaluation(nodes, open_nodes_counter, **kwargs):  # pylint: disable=unused-argument
    return list(range(open_nodes_counter + len(nodes), open_nodes_counter, -1))


def random_evaluation(nodes, search_space, **kwargs):  # pylint: disable=unused-argument
    raise NotImplementedError()


def get_reference_node(node: Node, domain: Graph) -> Node:
    return domain.get_node(getattr(node, 'reference'))


def python_test(node: Node, domain: Graph, **kwargs) -> bool:
    test = getattr(get_reference_node(node, domain), 'test', None)
    if not test:
        return True
    try:
        return bool(eval(test['code'], kwargs))  # pylint: disable=eval-used
    except Exception as error:
        raise PythonCodeError(test.get('source', '???')) from error


def python_execution(node: Node, domain: Graph, **kwargs) -> bool:
    action = getattr(get_reference_node(node, domain), 'action', None)
    if action:
        try:
            eval(action['code'], kwargs)  # pylint: disable=eval-used
        except Exception as error:
            raise PythonCodeError(action.get('source', '???')) from error

SELECTION_MAX = SearchSpace.ORDER_BY_MAX
SELECTION_MIN = SearchSpace.ORDER_BY_MIN

DEFAULT_POLICIES = {
    'generation': succesors_generation,
    'test': python_test,
    'selection': SELECTION_MAX,
    'execution': python_execution,
    'evaluation': order_evaluation,
}


def get_default_strategy(strategy):
    return DEFAULT_POLICIES[strategy]

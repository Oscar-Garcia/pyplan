# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
import random

import pytest

from ..pyplan.graph import Graph, SearchSpace


@pytest.fixture
def graph():
    return Graph()


@pytest.fixture
def search_space():
    return SearchSpace()


def test_graph(graph):
    node_a = graph.create_node()
    node_b = graph.create_node(in_nodes=node_a)
    node_c = graph.create_node(in_nodes=node_a)

    assert graph.is_successor(node_b, node_a)
    assert graph.is_successor(node_c, node_a)
    assert node_b in list(graph.successors(node_a))
    assert node_c in list(graph.successors(node_a))
    assert node_a in list(graph.predecessors(node_b))
    assert node_a in list(graph.predecessors(node_c))


def test_search_space(search_space):
    nodeb = search_space.node_builder
    nodes = [nodeb(node_id=i, weight=i) for i in range(1, 5)]
    assert search_space.get_len_open_nodes() == 0
    random.shuffle(nodes)
    for node in nodes:
        search_space.open_node(node)

    assert search_space.get_len_open_nodes() == 4

    current_weight = 10
    for node in search_space.get_open_nodes():
        assert current_weight > node.weight
        current_weight = node.weight
    assert current_weight == 1

    search_space.close_node(search_space.get_node(2))
    assert search_space.get_len_open_nodes() == 3
    assert next((node for node in search_space.get_open_nodes() if node.node_id == 2), None) is None
    search_space.open_node(nodeb(node_id=10, weight=10))
    search_space.open_node(nodeb(node_id=11, weight=10))
    assert search_space.get_len_open_nodes() == 5

    open_nodes = search_space.get_open_nodes()
    assert next(open_nodes).node_id == 11
    assert next(open_nodes).node_id == 10

    for node in search_space.get_open_nodes():
        search_space.close_node(node)

    assert search_space.get_len_open_nodes() == 0

# -*- coding: utf-8 -*-
import bisect
from functools import partialmethod

from .nodes import Node
from .serializers import NodeSerializer, get_default_node_serializer
from .store import CollectionMap, get_default_collection


class Graph(object):
    """
    This is the base class for a graph data structure.
    This implementation is using adjacent lists in order to save node relations.
    """

    def __init__(self, collection: CollectionMap=None, node_serializer: NodeSerializer=None):
        """
        Initializes the graph.
        Parameters:
            collection(CollectionMap): Is the collection used to save/load graph nodes.
            node_serializer(NodeSerializer): Is the serializer to load/save nodes form the collection.
        """
        self._collection = collection or get_default_collection()
        self._node_serializer = node_serializer or get_default_node_serializer()
        self._nodes_in_use = {}

    def __iter__(self):
        """
        Implements iterable protocol, this operation may be slow.
        """
        return self._collection.all_nodes()

    def create_node(self, node_id=None, in_nodes=None, out_nodes=None, **kwargs):
        """
        Adds a new node to the graph strcuture.
        Parameters:
            node_id(object): Is a unique identifier for the node, will be used as key for the collection.
            in_nodes(list): A list of nodes with arcs to the node being created.
            out_nodes(list): A list of nodes with arcs from the node being created.
            kwargs(dict): Extra fields passed to the node creation.
        Returns:
            Node: The node just created.
        """
        node_id = node_id or self._collection.next_id()
        node = self._node_serializer.from_data(self, node_id, **kwargs)
        node.graph = self
        self._collection.insert_record(node_id, self._node_serializer.to_data(node))
        if in_nodes:
            self.create_relationships(in_nodes, node)
        if out_nodes:
            self.create_relationships(node, out_nodes)
        self._nodes_in_use[node_id] = node
        return node

    def create_relationships(self, source_nodes, target_nodes):
        """
        Creates arcs from source_nodes to_target_nodes s*t.
        Parameters:
            source_nodes(list or Node): Nodes origin of the arc.
            target_nodes(list or Node): Nodes destination of the arc.
        """
        source_nodes = (source_nodes,) if isinstance(source_nodes, Node) else source_nodes
        target_nodes = (target_nodes,) if isinstance(target_nodes, Node) else target_nodes
        for source_node in source_nodes:
            for target_node in target_nodes:
                self.create_relationship(source_node, target_node)

    def create_relationship(self, source_node: Node, target_node: Node):
        """
        Creates an arc from source_node to_target_node.
        Parameters:
            source_node(Node): Node origin of the arc.
            target_node(Node): Node destination of the arc.
        """
        if target_node.node_id not in source_node.out_nodes_ids:
            source_node.out_nodes_ids.add(target_node.node_id)
            self._collection.put_record(source_node.node_id, self._node_serializer.to_data(source_node))
        if source_node.node_id not in target_node.in_nodes_ids:
            target_node.in_nodes_ids.add(source_node.node_id)
            self._collection.put_record(target_node.node_id, self._node_serializer.to_data(target_node))

    def update_node(self, node: Node):
        self._collection.put_record(node.node_id, self._node_serializer.to_data(node))

    def update_nodes(self, nodes):
        for node in nodes:
            self.update_node(node)

    def has_relationship(self, source_node: Node, target_node: Node) -> bool:  # pylint: disable=no-self-use
        """
        Checks if there is a connection from source_node to target_node.
        """
        return source_node.node_id in target_node.in_nodes_ids

    def get_node(self, node_id) -> Node:
        """
        Finds a node by its node_id.
        Parameters:
            node_id(object): Node identifier.
        Returns:
            Node: The found node.
        Raises:
            KeyError: If the node_id is invalid.
        """
        return self._node_serializer.from_data(graph=self, **self._collection.get_record(node_id))

    def get_nodes(self, ids):
        """
        Gets a generator of nodes finding them by its node_id. See get_node.
        """
        return (self.get_node(node_id) for node_id in ids)

    def is_successor(self, child_node: Node, parent_node: Node) -> bool:
        """
        Checks if child_node is a successor of parent_node.
        """
        return self.has_relationship(parent_node, child_node)

    def is_predecessor(self, parent_node: Node, child_node: Node) -> bool:
        """
        Checks if parent_node is predecessor of child_node.
        """
        return self.has_relationship(parent_node, child_node)

    def successors(self, node: Node):
        """
        Returns a generator over the successor `Node` of node.
        """
        return iter(self.get_node(node_id) for node_id in node.out_nodes_ids)

    def predecessors(self, node: Node):
        """
        Returns a generator over the predecessor `Node` of node.
        """
        return iter(self.get_node(node_id) for node_id in node.in_nodes_ids)

    node_builder = partialmethod(create_node)
    """This adds some syntax sugar in order to create a kind of DSL"""


class SearchSpace(Graph):
    ORDER_BY_MAX = 'max'
    ORDER_BY_MIN = 'min'

    def __init__(self, collection: CollectionMap=None, node_serializer: NodeSerializer=None, selector=None):
        super().__init__(collection, node_serializer)
        self.selector = selector or self.ORDER_BY_MAX

        self.open_nodes = []
        self.weights = []

    def get_len_open_nodes(self):
        return len(self.open_nodes)

    def open_node(self, node):
        bfunc = bisect.bisect_right if self.selector == self.ORDER_BY_MAX else bisect.bisect_left
        index = bfunc(self.weights, node.weight)
        self.open_nodes.insert(index, node.node_id)
        self.weights.insert(index, node.weight)

    def close_node(self, node):
        index = bisect.bisect_left(self.weights, node.weight)

        while not self.open_nodes[index] == node.node_id:
            index += 1
        self.open_nodes.pop(index)
        self.weights.pop(index)

    def close_all(self):
        self.open_nodes.clear()
        self.weights.clear()

    def get_open_nodes(self):
        open_nodes = reversed(self.open_nodes) if self.selector == self.ORDER_BY_MAX else self.open_nodes
        return (self.get_node(node_id) for node_id in open_nodes)

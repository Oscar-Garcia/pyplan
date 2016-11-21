# -*- coding: utf-8 -*-


class Node(object):
    """
    This class represents a node in a `Graph`. A node is an entity in the domain or in the search space that is
    connected with other nodes trough a Graph.
    """
    repr_fields = ('node_id', 'weight', 'reference')

    def __init__(self, graph, node_id, in_nodes_ids=None, out_nodes_ids=None):
        self.node_id = node_id
        self.graph = graph
        self.in_nodes_ids = set(in_nodes_ids or ())
        self.out_nodes_ids = set(out_nodes_ids or ())

    def __eq__(self, node):
        return isinstance(node, Node) and node.node_id == self.node_id

    def __repr__(self):
        generator = ("'%s': %s" % (field, getattr(self, field)) for field in self.repr_fields if hasattr(self, field))
        fields = ",".join(generator)
        return "%s(%s)" % (self.__class__.__name__, fields)

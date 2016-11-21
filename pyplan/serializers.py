# -*- coding: utf-8 -*-
from abc import abstractmethod
from functools import partial

import marshal

from .config import DEBUG_MODE
from .decorators import inherit_doc
from .nodes import Node
from .parser import PyParser


class FieldSerializationError(Exception):
    """
    This exception is raised when some error is detected during a node field serialization.
    Typical errors are Python syntax errors.
    """

    def __init__(self, field_name, data, error):
        self.field_name = field_name
        self.data = data
        self.error = error

    def __str__(self):
        lines = self.data.split('\n')
        if len(lines) >= self.error.lineno:
            line = lines[self.error.lineno - 1]
        else:
            line = self.data
        error_msg = '%d:%d: "%s"... %s' % (self.error.lineno, self.error.offset, self.error.msg, line)
        return 'Error on field "%s":%s' % (self.field_name, error_msg)


class NodeSerializationError(Exception):
    """
    This exception is raised when the serialization of a `Node` fails. The exception may contain
    other nested errors with more specific information, e.g. `FieldSerializationError`
    """

    def __init__(self, node, errors):
        self.node = node
        self.errors = errors

    def __str__(self):
        error_messages = '\n   >> '.join(str(error) for error in self.errors)
        return 'Errors while reading node "%s":\n   >> %s' % (str(self.node.node_id), error_messages)


class FieldSerializer(object):
    """
    This is an abstract class with the methods needed to serialize a field in a `Node`.
    """

    @abstractmethod
    def from_data(self, node, data):
        """
        Creates a field with the information given on data.
        Parameters:
            node(Node): Is the node under construction, where the field is going to be added.
            data(object): Contains all the information that need to be serialized.
        Returns:
            object: The contents of the field.
        """
        raise NotImplementedError()

    @abstractmethod
    def to_data(self, node):
        """
        This is the from_data inverse method, given a node, search for the field information in order to
        create a data structure that can be serialized.
        Parameters:
            node(Node): Is the node that is going to be serialized.
        Returns:
            object: Field data that can be serialized.
        """
        raise NotImplementedError()


class NodeSerializer(object):
    """
    This is a serializer for the ´Node´ class. Different ´FieldSerializer´ can be passed as parameters
    during the serializer initialization in order to inject how different fields of the node should be
    loaded or saved.
    """

    def __init__(self, field_serializers=None):
        """
        Initializes the serializer.
        Parameters:
            field_serializers(dict): A dictionary where the keys are the names of the fields to serialize and
            the values are the `FieldSerializer` to use.
        """
        self.field_serializers = field_serializers or {}

    def from_data(self, graph, node_id, in_nodes_ids=None, out_nodes_ids=None, **kwargs) -> Node:
        """
        Creates a new `Node` using the given data.

        Parameters:
            graph(Graph): The graph where the created node belongs to.
            node_id(object): A unique identifier for the node in the `Graph`.
            in_nodes_ids(list, object): A list of `Node` with arcs to the created node.
            out_nodes(list, object): A list of `Node` with arcs from the created node.
            kwargs(dict): Extra information passed to the node.

        Returns:
            Node: The created node.
        """
        node = Node(graph, node_id, in_nodes_ids, out_nodes_ids)
        self.fields_from_data(node, kwargs)
        return node

    def to_data(self, node):
        """
        Converts a `Node` into data that can be serialized and saved in a `CollectionMap`
        Parameters:
            node(Node): Is the node that is going to be serialized.
        Returns:
            object: Data to be saved in a collection or to be send to another service.
        """
        data = self.fields_to_data(node)
        data['node_id'] = node.node_id
        data['in_nodes_ids'] = list(node.in_nodes_ids)
        data['out_nodes_ids'] = list(node.out_nodes_ids)
        return data

    def fields_from_data(self, node, data):
        errors = []
        for key, value in data.items():
            if key in self.field_serializers:
                try:
                    serializer = self.field_serializers[key]
                    if serializer:
                        value = serializer.from_data(node, value)
                    setattr(node, key, value)
                except FieldSerializationError as error:
                    errors.append(error)
        if errors:
            raise NodeSerializationError(node, errors)

    def fields_to_data(self, node):
        data = {}
        for key, serializer in self.field_serializers.items():
            value = serializer.to_data(node) if serializer else getattr(node, key, None)
            if value is not None:
                data[key] = value
        return data


@inherit_doc
class FunctionFieldSerializer(FieldSerializer):
    """
    This serializer manages the serialization of fields whose content is Python evaluable code.
    If DEBUG_MODE is on we will also collection the source code on the field.
    """

    def __init__(self, field_name, parser=None):
        self.field_name = field_name
        self.parser = parser or PyParser()

    def from_data(self, node, data):
        if data is None:
            return None

        if isinstance(data, dict):
            if 'code' in data:
                return {
                    'code': marshal.loads(data['code']),
                    'source': data.get('source', None) if DEBUG_MODE else None
                }
        if isinstance(data, str):
            try:
                node = self.parser.parse_python(data)
                return {
                    'code': node.code,
                    'source': node.source if DEBUG_MODE else None
                }
            except SyntaxError as error:
                raise FieldSerializationError(self.field_name, data, error)

        raise NotImplementedError('Unsupported data %s' % str(data))

    def to_data(self, node):
        func = getattr(node, self.field_name, None)
        if not func:
            return
        return {
            'code': marshal.dumps(func['code']),
            'source': func.get('source', None) if DEBUG_MODE else None
        }


FIELD_SERIALIZERS = {
    'test': partial(FunctionFieldSerializer, 'test'),
    'action': partial(FunctionFieldSerializer, 'action'),
    'reference': None,
    'weight': None,
    'context_id': None
}


def init_field_serializer(ser, parser):
    return ser(parser) if ser else None


def field_serializers(serializer_names, parser):
    return {name: init_field_serializer(FIELD_SERIALIZERS[name], parser) for name in serializer_names}


def get_default_node_serializer(parser=None):
    """
    This function gets the default field serializers for some kind of predefined fields.
    """
    return NodeSerializer(field_serializers=field_serializers(FIELD_SERIALIZERS.keys(), parser))

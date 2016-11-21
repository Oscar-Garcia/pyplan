# -*- coding: utf-8 -*-
from ..pyplan.serializers import FunctionFieldSerializer, NodeSerializer


def test_function_serializer():
    serializer = FunctionFieldSerializer('test_field')

    field = serializer.from_data(None, '5 + 5')
    assert 'code' in field
    assert eval(field['code']) == 10  # pylint: disable=eval-used


def test_node_serializer():
    serializer = NodeSerializer({'test': FunctionFieldSerializer('test')})
    node = serializer.from_data(graph=None, node_id=1, test='5+5')
    assert node is not None
    assert eval(node.test['code']) == 10  # pylint: disable=eval-used, no-member

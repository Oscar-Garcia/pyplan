# -*- coding: utf-8 -*-
import types


def inherit_doc(cls):
    """
    This decorator simply add docstrings from parent class to subclass methods if no documentation
    exists on the subclass method.
    """
    for name, func in vars(cls).items():
        if isinstance(func, types.FunctionType) and not func.__doc__:
            for parent in cls.__bases__:
                parfunc = getattr(parent, name, None)
                if parfunc and getattr(parfunc, '__doc__', None):
                    func.__doc__ = parfunc.__doc__
                    break
    return cls

# -*- coding: utf-8 -*-
from functools import partial

from .graph import SearchSpace
from .store import ScopeStore


def sget(key, *args, frame=None):
    try:
        return frame.context.get_record(key)
    except KeyError:
        if len(args) == 1:
            return args[0]
        raise


def sput(key, value, frame=None):
    return frame.w_context.put_record(key, value)


def sput_all(key, value, frame=None):
    return frame.store.init.put_record(key, value)


class Frame(object):  # pylint: disable=too-many-instance-attributes

    ro_keys = ('node_counter', 'open_nodes_counter',)
    INIT_CONTEXT_ID = -1

    def __init__(self, solver, store: ScopeStore, search_space: SearchSpace):
        self.solver = solver
        self.search_space = search_space
        self.store = store
        self.node_counter = 0
        self.selected = None
        self.context = self.store.init
        self.ro_builtins = solver.builtins or {}
        self.ro_builtins['logger'] = solver.logger
        self.ro_builtins['sget'] = partial(sget, frame=self)
        self.w_builtins = dict(self.ro_builtins)
        self.w_builtins['sput'] = partial(sput, frame=self)
        self.w_builtins['sput_all'] = partial(sput_all, frame=self)
        self._init_builtins()

    def _init_builtins(self):
        self.ro_builtins['node_counter'] = self.node_counter
        self.ro_builtins['open_nodes_counter'] = self.search_space.get_len_open_nodes()
        for key in self.ro_keys:
            self.w_builtins[key] = self.ro_builtins[key]

    def next_frame(self):
        self.node_counter += 1
        context_id = self.selected.context_id
        self.context = self.store.get_scope(context_id) if context_id != self.INIT_CONTEXT_ID else self.store.init
        self._init_builtins()

    @property
    def final_context(self):
        return self.context

    @property
    def final_node(self):
        return self.selected

    @property
    def w_context(self):
        if self.selected.context_id != self.selected.node_id:
            if self.selected.context_id != self.INIT_CONTEXT_ID:
                self.context = self.store.create_scope(self.selected.node_id, self.selected.context_id)
            else:
                self.context = self.store.create_scope(self.selected.node_id)
            self.selected.context_id = self.selected.node_id
            self.search_space.update_node(self.selected)
        return self.context

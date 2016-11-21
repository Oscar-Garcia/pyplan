# -*- coding: utf-8 -*-
from .builtins import Frame
from .graph import Graph, SearchSpace
from .logger import get_default_logger
from .store import ScopeStore, get_default_scope_store
from .strategies import get_default_strategy


class NoMoreNodesError(Exception):
    """
    This exception is launched when a node generator is exhausted.
    """
    pass


class MaxNodesReachedError(Exception):
    """
    This exception is raised when the maximum number of allowed nodes is reached during the search.
    """
    def __init__(self, node_counter):
        super().__init__()
        self.node_counter = node_counter

    def __repr__(self):
        return '%s(Number of nodes: %d)' % (self.__class__.__name__, self.node_counter)


class Solver(object):  # pylint: disable=too-many-instance-attributes
    """
    This class represents a generic problem solver. The Solver represents its search space using a `Graph`,
    each `Node` in the graph represent a decision to be made or an action to be executed.
    The way the Solver is configured is through different search/test/selection/execution strategies that can
    be configured.
    Attributes:
        domain(Graph): Is the domain representing the set of nodes defining how the search is done. Each of this
            nodes is instantiated and added to the search space graph.
        is_solution(function): A function to call to check if a solution has been found.
        evaluator(function): Is a function that assigns weights to the nodes being evaluated at the current
            search step.
        selector(function): Is a selection operator to choose one node once they have been weighted.
        test(function): Is a function to check if a testable node is true or not.
        execute(function): Is a function to execute an actionable node.
        expand(function): Is a method that given the current node in the search space, generates the next
            set of nodes that need to be evaluated.
        logger(Logger): Is the logger used to print information about the search.
        max_nodes(int): Is a limit over the maximum number of nodes to generate, when this number is reached
            a `MaxNodesReachedError` exception is raised.
        backtrack(bool): Where backtracking can be used or not to explore previously discarded nodes on
            the search space.
    """

    def __init__(self, domain: Graph, solution_checker):
        self.domain = domain
        self.is_solution = solution_checker
        self.evaluator = get_default_strategy('evaluation')
        self.selector = get_default_strategy('selection')
        self.test = get_default_strategy('test')
        self.execute = get_default_strategy('execution')
        self.expand = get_default_strategy('generation')
        self.logger = get_default_logger()
        self.max_nodes = None
        self.builtins = None
        self.backtrack = True

    def create_init_frame(self, store: ScopeStore=None, search_space: Graph=None):
        return Frame(self, store, search_space)

    def eval(self, *args, store: ScopeStore=None, search_space: Graph=None):
        current_nodes = args
        search_space = search_space or SearchSpace(selector=self.selector)
        store = store or get_default_scope_store()
        frame = self.create_init_frame(store, search_space)
        while not self.is_solution(**frame.ro_builtins):
            current_nodes = self.step(current_nodes, frame, search_space)
            frame.next_frame()
        return frame

    def step(self, current_nodes, frame: Frame, search_space: Graph):
        if frame.node_counter == self.max_nodes:
            raise MaxNodesReachedError(frame.node_counter)
        self.logger.debug('Number of expanded nodes: %d', frame.node_counter)
        instances = self.instantiate(current_nodes, frame, search_space)
        self.logger.debug('Instances: %s', instances)
        self.eval_nodes(instances, frame, search_space)
        frame.selected = self.select(frame, search_space)
        # manage deltas here, changes on the context
        self.logger.debug('Selected Node: %s', frame.selected)
        self.execute(node=frame.selected, domain=self.domain, **frame.w_builtins)
        if not self.backtrack:
            search_space.close_all()
        return self.expand(node=frame.selected, domain=self.domain)

    def instantiate(self, dmn_nodes, frame: Frame, search_space: Graph):  # pylint: disable=no-self-use
        parent = frame.selected
        snode = search_space.node_builder
        context_id = parent.context_id if parent else frame.INIT_CONTEXT_ID
        return list(snode(reference=node.node_id, in_nodes=parent, context_id=context_id) for node in dmn_nodes)

    def eval_nodes(self, instances, frame: Frame, search_space: Graph):
        parent = frame.selected
        evaluations = self.evaluator(parent=parent, nodes=instances, **frame.ro_builtins)
        self.logger.debug('New nodes weights: %s', evaluations)
        for node, weight in zip(instances, evaluations):
            if weight is not None:
                # discard those modules that have not been weighted
                setattr(node, 'weight', weight)
                search_space.update_node(node)
                search_space.open_node(node)

    def select(self, frame: Frame, search_space: Graph):
        for selection in search_space.get_open_nodes():
            test = self.test(selection, domain=self.domain, **frame.ro_builtins)
            self.logger.debug("Test of %s is %s", selection, test)
            search_space.close_node(selection)
            if test:
                return selection
        raise NoMoreNodesError()

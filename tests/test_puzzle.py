# -*- coding: utf-8 -*-
"""
This set of tests demonstrates how to solve N-Puzzle problems using the PyPlan library.

The puzzle is a board game for a single player. It consists of numbered squared tiles in random order,
and one blank space ("a missing tile"). The object of the puzzle is to rearrange the tiles in order by
making sliding moves that use the empty space, using the fewest moves.
Moves of the puzzle are made by sliding an adjacent tile into the empty space.
Only tiles that are horizontally or vertically adjacent to the blank space (not diagonally adjacent) may be moved.
"""
from .puzzle import Puzzle
from ..pyplan.solver import Solver
from ..pyplan.store import get_default_scope_store
from ..pyplan.graph import Graph
from ..pyplan.strategies import SELECTION_MIN


def get_puzzle(sget):
    return Puzzle(height=sget('height'), width=sget('width'), puzzle=sget('puzzle'))


def is_solution(sget, **kwargs):
    puzzle = get_puzzle(sget)
    return puzzle.is_solved()


def distance(puzzle, current_position, expected_position):
    col_i, row_i = puzzle.get_coordinates(current_position)
    col_j, row_j = puzzle.get_coordinates(expected_position)
    return abs(col_i - col_j) + abs(row_i - row_j)


def manhattan_distance(puzzle):
    return sum(distance(puzzle, puzzle.get_position(i), i) for i in range(1, puzzle.size))


def row_conflicts(puzzle):
    conflicts = 0
    for row in range(0, puzzle.height):
        min_range = row*puzzle.width
        max_range = min_range + puzzle.width
        for col1 in range(0, puzzle.width):
            tile1 = puzzle.get_tile(col1, row)
            if tile1 != 0 and tile1 >= min_range and tile1 < max_range:
                for col2 in range(col1 + 1, puzzle.width):
                    tile2 = puzzle.get_tile(col2, row)
                    if tile2 != 0 and tile2 >= min_range and tile2 < max_range:
                        if tile1 > tile2:
                            conflicts += 1
    return conflicts


def col_conflicts(puzzle):
    conflicts = 0
    for col in range(0, puzzle.width):
        valid_values = frozenset((col + index*puzzle.width for index in range(0, puzzle.height)))
        for row1 in range(0, puzzle.height):
            tile1 = puzzle.get_tile(col, row1)
            if tile1 != 0 and tile1 in valid_values:
                for row2 in range(row1 + 1, puzzle.height):
                    tile2 = puzzle.get_tile(col, row2)
                    if tile2 != 0 and tile2 in valid_values:
                        if tile1 > tile2:
                            conflicts += 1
    return conflicts


def linear_conflicts(puzzle):
    return row_conflicts(puzzle) + col_conflicts(puzzle)


def is_inverse(move_a, move_b):
    if move_a == Puzzle.RIGHT and move_b == Puzzle.LEFT:
        return True
    elif move_a == Puzzle.LEFT and move_b == Puzzle.RIGHT:
        return True
    elif move_a == Puzzle.UP and move_b == Puzzle.DOWN:
        return True
    elif move_a == Puzzle.DOWN and move_b == Puzzle.UP:
        return True
    else:
        return False


def is_explored(sget, new_puzzle):
    explored = sget('explored', {})
    blank = new_puzzle.get_blank_position()
    explored = explored.get(blank, None)
    return new_puzzle in explored if explored else False


def manhattan_heuristic(parent, nodes, sget, **kwargs):
    puzzle = get_puzzle(sget)
    weights = []
    previous_move = parent.reference if parent else None
    for node in nodes:
        move_ref = node.reference
        blank = puzzle.get_blank_position()
        if puzzle.can_move(move_ref, blank) and not is_inverse(move_ref, previous_move):
            next_puzzle = puzzle.move(move_ref, blank)
            if not is_explored(sget, next_puzzle):
                weights.append(manhattan_distance(next_puzzle) + 2*linear_conflicts(next_puzzle))
            else:
                weights.append(None)
        else:
            weights.append(None)
    return weights


def can_move(sget, movement):
    puzzle = get_puzzle(sget)
    return puzzle.can_move(movement)


def move(sget, sput, sput_all, logger, movement):
    puzzle = get_puzzle(sget)
    movements = sget('movements', 0)
    new_puzzle = puzzle.move(movement)
    blank = new_puzzle.get_blank_position()
    sput('puzzle', new_puzzle.to_list())
    sput('movements', movements + 1)
    explored = sget('explored', {})
    explored.setdefault(blank, []).append(new_puzzle.to_list())
    sput_all('explored', explored)
    logger.debug('New puzzle: %s', new_puzzle)


def create_movement(node, movement):
    return node(
        node_id=movement,
        test=('can_move(sget, "%s")' % movement),
        action=('move(sget, sput, sput_all, logger, "%s")' % movement)
    )


def test_is_solved():
    puzzle = Puzzle(2, 2)
    assert puzzle.is_solved()


def test_is_not_solved():
    puzzle = Puzzle(2, 2)
    puzzle.shuffle(steps=2, seed=23)
    assert not puzzle.is_solved()


def test_get_tile():
    puzzle = Puzzle(2, 2)
    assert puzzle.get_tile(0, 0) == 0
    assert puzzle.get_tile(1, 0) == 1
    assert puzzle.get_tile(0, 1) == 2
    assert puzzle.get_tile(1, 1) == 3


def test_movements():
    puzzle = Puzzle(height=4, width=3)
    assert puzzle.can_move(puzzle.DOWN, 0)
    assert not puzzle.can_move(puzzle.DOWN, 9)
    assert not puzzle.can_move(puzzle.DOWN, 11)
    assert puzzle.can_move(puzzle.UP, 11)
    assert not puzzle.can_move(puzzle.UP, 0)
    assert not puzzle.can_move(puzzle.UP, 2)
    assert not puzzle.can_move(puzzle.LEFT, 0)
    assert not puzzle.can_move(puzzle.LEFT, 9)
    assert puzzle.can_move(puzzle.LEFT, 4)
    assert puzzle.can_move(puzzle.LEFT, 11)
    assert puzzle.can_move(puzzle.LEFT, 2)
    assert not puzzle.can_move(puzzle.RIGHT, 2)
    assert not puzzle.can_move(puzzle.RIGHT, 11)
    assert puzzle.can_move(puzzle.RIGHT, 0)
    assert puzzle.can_move(puzzle.RIGHT, 9)


def test_manhattan():
    puzzle = Puzzle(height=2, width=2)
    assert manhattan_distance(puzzle) == 0

    puzzle = Puzzle(height=2, width=2, puzzle=[1, 0, 2, 3])
    assert manhattan_distance(puzzle) == 1

    puzzle = Puzzle(height=4, width=4, puzzle=[15, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 13, 14, 12])
    assert manhattan_distance(puzzle) == 9


def test_linear_conflicts():
    puzzle = Puzzle(height=1, width=3, puzzle=[0, 2, 1])
    assert linear_conflicts(puzzle) == 1

    puzzle = Puzzle(height=3, width=1, puzzle=[0, 2, 1])
    assert linear_conflicts(puzzle) == 1

    puzzle = Puzzle(height=3, width=3, puzzle=[0, 1, 2, 3, 5, 4, 5, 7, 8])
    assert linear_conflicts(puzzle) == 1

    puzzle = Puzzle(height=3, width=3, puzzle=[0, 1, 2, 3, 4, 8, 6, 7, 5])
    assert linear_conflicts(puzzle) == 1


def test_solve_puzzle():
    """
    Implements a IDA* (Iterative Deepening A*)
    to solve an example of 8-puzzle.
    """
    height = 3
    width = 3
    puzzle = Puzzle(height, width)
    puzzle.shuffle(steps=5, seed=13)
    assert not puzzle.is_solved()
    store = get_default_scope_store()
    context = store.init
    context.insert_record('puzzle', puzzle.to_list())
    context.insert_record('height', height)
    context.insert_record('width', width)
    domain = Graph()
    node = domain.node_builder

    # generate movements
    movements = [create_movement(node, movement) for movement in puzzle.movements]

    for movement in movements:
        domain.create_relationships(movement, movements)

    builtins = {
        'can_move': can_move,
        'move': move
    }
    solver = Solver(domain, is_solution)
    solver.evaluator = manhattan_heuristic
    solver.selector = SELECTION_MIN
    solver.builtins = builtins
    solver.max_nodes = 400000

    solver.logger.debug('Initial puzzle: %s', puzzle)
    solution = solver.eval(*movements, store=store)

    puzzle = Puzzle(height, width, solution.final_context.get_record('puzzle'))
    assert puzzle.is_solved()

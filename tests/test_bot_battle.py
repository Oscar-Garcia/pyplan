# -*- coding: utf-8 -*-
"""
This set of tests demonstrates how to implement a simple behavior tree
for a simulated bot battle game. For the moment the sample only has one level of nodes.
"""
import random

# pylint: disable=redefined-outer-name
import pytest

from ..pyplan.graph import Graph
from ..pyplan.solver import Solver
from ..pyplan.store import get_default_scope_store


@pytest.fixture
def store():
    sstore = get_default_scope_store()
    context = sstore.init
    # our board is composed of squared tiles
    context.insert_record('arena', {'height': 25, 'width': 25})
    context.insert_record('bot_ids', ['bender', 'c3po'])
    bender = {
        'id': 'bender',
        'x': 5,
        'y': 5,
        'range': 3,
        'sight': 5,
        'damage': 7,
        'max_health': 50,
        'health': 50,
        'movements': 3
    }
    c3po = {
        'id': 'c3po',
        'x': 15,
        'y': 5,
        'range': 3,
        'sight': 7,
        'damage': 3,
        'max_health': 30,
        'health': 30,
        'movements': 3
    }
    context.insert_record('bender', bender)
    context.insert_record('c3po', c3po)
    return sstore


def get_current_bot(sget):
    bot = sget('turn')
    return sget(bot)


def is_alive(bot):
    return bot['health'] > 0


def next_on(key, current, sget):
    bot_ids = sget('bot_ids')
    other_bots = (sget(bot_id) for bot_id in bot_ids if bot_id != current['id'])
    return next((bot for bot in other_bots if is_alive(bot) and distance(current, bot) <= current[key]), None)


def distance(one_bot, another_bot):
    # this is a rough simplification
    return (abs(one_bot['x'] - another_bot['x']) + abs(one_bot['y'] - another_bot['y']))/2


def enemy_onrange(sget):
    current = get_current_bot(sget)
    return next_on('range', current, sget) is not None


def enemy_onsight(sget):
    current = get_current_bot(sget)
    return next_on('sight', current, sget) is not None


def healthy(sget):
    current = get_current_bot(sget)
    return current['health'] > current['max_health']*0.2


def attack(sget, sput, logger):
    current = get_current_bot(sget)
    other = next_on('range', current, sget)
    other['health'] = other['health'] - current['damage']
    sput(other['id'], other)
    sput('turn', None)
    logger.info('%s ATTACKS %s!. %s health is %d', current['id'], other['id'], other['id'], other['health'])


def approach(sget, sput, logger):
    current = get_current_bot(sget)
    other = next_on('sight', current, sget)
    move(current, other['x'], other['y'], sget, sput, logger)


def flee(sget, sput, logger):
    current = get_current_bot(sget)
    other = next_on('sight', current, sget)
    move(current, other['x'], other['y'], sget, sput, logger, inc=-1)


def wander(sget, sput, logger):
    current = get_current_bot(sget)
    arena = sget('arena')
    pos_x = random.randint(0, arena['height'] - 1)
    pos_y = random.randint(0, arena['width'] - 1)
    move(current, pos_x, pos_y, sget, sput, logger, inc=-1)


def can_move(arena, pos_x, pos_y):
    return arena['height'] > pos_x >= 0 and arena['width'] > pos_y >= 0


def move(current, target_x, target_y, sget, sput, logger, inc=1):  # pylint: disable=too-many-arguments
    current_x = current['x']
    current_y = current['y']
    arena = sget('arena')
    for _ in range(0, current['movements']):
        if current_x < target_x and can_move(arena, current_x + inc, current_y):
            current_x += inc
        elif current_y < target_y and can_move(arena, current_x, current_y + inc):
            current_y += inc
        elif current_x > target_x and can_move(arena, current_x - inc, current_y):
            current_x -= inc
        elif current_y > target_y and can_move(arena, current_x, current_y - inc):
            current_y -= inc
    current['x'] = current_x
    current['y'] = current_y
    sput(current['id'], current)
    sput('turn', None)
    logger.info('%s MOVES to position (%d, %d)', current['id'], current_x, current_y)


@pytest.fixture
def domain():
    dom = Graph()
    node = dom.node_builder
    node(
        node_id='attack',
        test=('enemy_onrange(sget) and healthy(sget)'),
        action=('attack(sget, sput, logger)')
    )
    node(
        node_id='approach',
        test=('enemy_onsight(sget) and healthy(sget) and not enemy_onrange(sget)'),
        action=('approach(sget, sput, logger)')
    )
    node(
        node_id='flee',
        test=('enemy_onsight(sget) and not healthy(sget)'),
        action=('flee(sget, sput, logger)')
    )
    node(
        node_id='wander',
        test=('not enemy_onsight(sget)'),
        action=('wander(sget, sput, logger)')
    )
    return dom


def is_solution(sget, **kwargs):  # pylint: disable=unused-argument
    return sget('turn') is None


def is_dead(context):
    return not is_alive(context.get_record('c3po')) or not is_alive(context.get_record('bender'))


def test_battle(store, domain):
    random.seed(0)
    solver = Solver(domain, is_solution)
    builtins = {
        'enemy_onsight': enemy_onsight,
        'enemy_onrange': enemy_onrange,
        'approach': approach,
        'flee': flee,
        'healthy': healthy,
        'attack': attack,
        'wander': wander,
        'move': move
    }
    solver.builtins = builtins
    solver.backtrack = False

    all_nodes = list(node for node in domain)
    context = store.init
    frame = None
    bots = ('c3po', 'bender')
    step = 0
    while not is_dead(context):
        context.insert_record('turn', bots[step % len(bots)])
        frame = solver.eval(*all_nodes, store=store, from_frame=frame)
        context = frame.context
        step += 1

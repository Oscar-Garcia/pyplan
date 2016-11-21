# -*- coding: utf-8 -*-
"""
This set of tests demonstrates how to implement a simple behavior tree
for a simulated bot battle game. For the moment the sample only has one level of nodes.
"""
import pytest
from ..pyplan.solver import Solver
from ..pyplan.store import get_default_scope_store
from ..pyplan.graph import Graph
from ..pyplan.strategies import SELECTION_MIN


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
        'movements': 1
    }
    c3po = {
        'id': 'c3po',
        'x': 15,
        'y': 5,
        'range': 3,
        'sight': 7,
        'damage': 1,
        'max_health': 30,
        'health': 30,
        'movements': 3
    }
    context.insert_record('bender', bender)
    context.insert_record('c3po', c3po)
    return store


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
    sput(other['key'], other)
    logger('%s ATTACKS %s!. %s health is %d', current['id'], other['id'], other['id'], other['health'])


def approach(sget, sput, logger):
    current = get_current_bot(sget)
    other = next_on('sight', current, sget)
    move(current, other['x'], other['y'], sput, logger)


def move(current, target_x, target_y, sput, logger):
    current_x = current['x']
    current_y = current['y']
    for _ in range(0, current['movements']):
        if current_x < target_x:
            current_x += 1
        elif current_y < target_y:
            current_y += 1
        elif current_x > target_x:
            current_x -= 1
        elif current_y > target_y:
            current_y -= 1
    current['x'] = current_x
    current['y'] = current_y
    sput(current['key'], current)
    logger('%s MOVES to position (%d, %d)', current[id], current_x, current_y)


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
        test=('enemy_onsight(sget) and healthy(sget)'),
        action=('aproach(sget, sput, logger)')
    )
    node(
        node_id='flee',
        test=('enemy_onsight(sget) and not healthy(sget)'),
        action=('flee(sget, sput, logger)')
    )
    node(
        node_id='wander',
        action=('wander(sget, sput, logger)')
    )
    return dom


def test_battle(store, domain):
    raise NotImplementedError()

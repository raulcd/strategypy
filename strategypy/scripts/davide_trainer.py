import json
import itertools
import operator
import random
import os.path
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game import Game
from bots.davide import Bot as DavideBot
import settings

settings.GRID_SIZE = (40, 40)
settings.UNITS = 10
settings.MAX_TURNS = 100
settings.RESPAWN = False
settings.BORDER = "WALL"


def play_game(rules):
    a, b, c, d = rules
    rules_dict = {
        'be_able_to_move': 100.0,
        'risk_of_dieing': a,
        'outnumber_isolated_enemies': b,
        'closer_to_central_mass': c,
        'find_isolated_targets': d,
    }
    DavideBot.rules = rules_dict

    game = Game('davide', 'happiness')
    result = game.main_loop()
    result = json.loads(result)

    davide_units = result['frames'][-1].get('0', [])
    is_davide_winner = result['winner'] == 0
    turns = result['turns']
    utility = len(davide_units) * is_davide_winner
    if utility > 0:
        utility += 1 - (turns/float(settings.MAX_TURNS))

    return utility


def play_games(rules, n=5):
    results = [play_game(rules) for _ in xrange(0, n)]
    avg = sum(results)/float(len(results))
    return avg


def max_from_dict(dictionary):
    k, v = max(
        dictionary.iteritems(),
        key=operator.itemgetter(1)
    )
    return k, v


def random_rules():
    return tuple(round(random.random() * 3, 2) for _ in xrange(0, 4))


def make_son(rules_one, rules_two):
    son = list(
        round((a + b)/float(2), 2)
        for a, b in zip(rules_one, rules_two)
    )
    # Mutate son
    for each in son:
        new_val = each + random.choice([-0.2, -0.1, 0, 0.2, 0.1])
        if new_val > 0:
            each += new_val
        else:
            each = 0

    return tuple(son)


# TRAININGS


def bruteforce_training():
    GAMES_TO_PLAY = 10

    values = set()
    values.update(set(itertools.permutations([10, 10, 10, 1])))
    values.update(set(itertools.permutations([10, 10, 5, 1])))
    values.update(set(itertools.permutations([10, 10, 1, 1])))
    values.update(set(itertools.permutations([10, 5, 5, 1])))
    values.update(set(itertools.permutations([10, 5, 2, 1])))
    values.update(set(itertools.permutations([10, 5, 1, 1])))
    values.update(set(itertools.permutations([10, 1, 1, 1])))
    values.update(set(itertools.permutations([2, 1, 1, 1])))
    values.update(set(itertools.permutations([2, 2, 2, 1])))
    values.update(set(itertools.permutations([2, 2, 1, 1])))
    values.update(set(itertools.permutations([3, 3, 3, 1])))
    values.update(set(itertools.permutations([3, 3, 2, 1])))
    values.update(set(itertools.permutations([3, 3, 1, 1])))
    values.update(set(itertools.permutations([1, 1, 1, 1])))

    n = len(values)
    print 'BRUTEFORCE TRAINING - {} rules'.format(n)
    result = {}
    for i, value in enumerate(values):
        result[value] = play_games(value, n=GAMES_TO_PLAY)
        per_cent = (i*100)/float(n)
        print '{:.1f}% - Played {} games with rule {}: {}'.format(
            per_cent, GAMES_TO_PLAY, value, result[value])
    return max_from_dict(result)


def random_training():
    GAMES_TO_PLAY = 10
    values = [random_rules() for _ in xrange(0, 100)]

    n = len(values)
    print 'RANDOM TRAINING - {} rules'.format(n)
    result = {}
    for i, value in enumerate(values):
        result[value] = play_games(value, n=GAMES_TO_PLAY)
        per_cent = (i*100)/float(n)
        print '{:.1f}% - Played {} games with rule {}: {}'.format(
            per_cent, GAMES_TO_PLAY, value, result[value])
    return max_from_dict(result)


def genetic_algorythms_training():
    AMOUNT_OF_SONS = 8
    GENETIC_POOL = 20
    GAMES_TO_PLAY = 20
    GENERATIONS = 10
    print 'RANDOM TRAINING - {} rules, {} generations'.format(
        GENETIC_POOL, GENERATIONS)
    print
    values = [random_rules() for _ in xrange(0, GENETIC_POOL)]
    for j, x in enumerate(xrange(0, GENERATIONS)):
        result = {}
        print 'Start generation {}'.format(j)
        for i, value in enumerate(values):
            result[value] = play_games(value, n=GAMES_TO_PLAY)
            per_cent =  \
                (100*(j*GENETIC_POOL + i))/float(GENERATIONS * GENETIC_POOL)
            print '{:.1f}% - Played {} games with rule {}: {}'.format(
                per_cent, GAMES_TO_PLAY, value, result[value])
        k_one, v_one = max_from_dict(result)
        result.pop(k_one)
        k_two, v_two = max_from_dict(result)
        sons = [make_son(k_one, k_two) for _ in xrange(0, AMOUNT_OF_SONS)]
        values = [
            random_rules()
            for _ in xrange(0, GENETIC_POOL - AMOUNT_OF_SONS)
        ]
        values.extend([k_one, k_two])
        values.extend(sons)
        print 'First best of generation {} is {} {} '.format(j, k_one, v_one)
        print 'Second best of generation {} is {} {} '.format(j, k_two, v_two)
        print

    return k_one, v_one

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("trainer", choices=['bruteforce', 'genetic', 'random'])
    funcs = {
        'bruteforce': bruteforce_training,
        'genetic': genetic_algorythms_training,
        'random': random_training,
    }
    arguments = parser.parse_args()
    print funcs[arguments.trainer]()

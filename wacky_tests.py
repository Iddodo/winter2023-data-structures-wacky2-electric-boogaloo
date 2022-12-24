#!/usr/bin/env python3

from Wacky2Unit import Wacky2Unit
from sympy.combinatorics.permutations import Permutation
import random
import os

# --- Custom variables for test generation --- #

num_players = 1000
num_teams = 100
num_commands = 1000
num_tests = 100
random_integer_upper_bound = 300

# --- Player and team ID lists --- #
initial_players = [i for i in range(1, num_players + 1)]
initial_teams = [i for i in range(1, num_teams + 1)]

players = initial_players.copy()
removed_players = []
teams = initial_teams.copy()
team_players = {ID: [] for ID in teams}

# --- Functions to fetch relevant random values --- #
def random_team_ID():
    return random.choice(teams)


def random_player_ID(include_removed=False):
    if include_removed:
        return random.choice(players + removed_players)

    return random.choice(players)


def random_positive_integer():
    return random.randint(1, random_integer_upper_bound)


def random_1to5_permutation():
    identity = [0, 1, 2, 3, 4]
    random.shuffle(identity)
    return Permutation(identity)


def new_team_ID():
    if not teams:
        return 1
    return max(teams) + 1


def new_player_ID():
    if not players:
        return 1
    return max(players) + 1


# --- Randomizing commands ---#

w = Wacky2Unit()

test_commands = [
    'add_team',
    'remove_team',
    'add_player',
    'play_match',
    'num_played_games_for_player',
    'add_player_cards',
    'get_player_cards',
    'get_team_points',
    'get_ith_pointless_ability',
    'sort_dicts_by_ability',
    'get_partial_spirit',
    'buy_team',
]

# Need a higher probability of adding players
test_commands += 2 * ['add_player']

def w_new_player(ID):
    r = [random_positive_integer() for i in range(0, 3)]
    team_ID = random_team_ID()
    w.add_player(ID, team_ID, random_1to5_permutation(), r[0], r[1], r[2], random.choice((True, False)))

    if 'SUCCESS' not in  w.expected[-1]:
        return

    players.append(ID)
    team_players[team_ID].append(ID)


# --- Implementation of runtime commands ---- #
# Commands with actual function names assure non-invalid input,
# and prevents trivial failure (some failure may still occur).
def execute_test_command(cmd):
    if cmd == 'add_team':
        w.add_team(new_team_ID())

    if cmd == 'remove_team':
        # Do not allow a team to be removed if only one team exists (annoying endcase)
        if len(teams) <= 1:
            return

        team_ID = random_team_ID()
        w.remove_team(team_ID)

        if 'SUCCESS' not in w.expected[-1]:
            return

        for player_ID in team_players[team_ID]:
            players.remove(player_ID)
            removed_players.append(player_ID)

        teams.remove(team_ID)
        del team_players[team_ID]

    if cmd == 'add_player':
        w_new_player(new_player_ID())

    if cmd == 'play_match':
        team1 = random_team_ID()
        team2 = random_team_ID()

        if len(teams) > 1:
            while (team2 == team1):
                team2 = random_team_ID()

        w.play_match(team1, team2)

    # Allow player IDs
    if cmd == 'num_played_games_for_player':
        w.num_played_games_for_player(
            random_player_ID(include_removed=True))

    # TODO: also test for removed players
    if cmd == 'add_player_cards':
        w.add_player_cards(random_player_ID(), random_positive_integer())

    if cmd == 'get_player_cards':
        w.get_player_cards(
            random_player_ID(include_removed=True))

    if cmd == 'get_team_points':
        w.get_team_points(random_team_ID())

    # TODO: problematic function, do more tests
    if cmd == 'get_ith_pointless_ability':
        w.get_ith_pointless_ability(random.randint(0, len(teams)))

    if cmd == 'get_partial_spirit':
        w.get_partial_spirit(random_player_ID())

    if cmd == 'buy_team':
        w.buy_team(random_team_ID(), random_team_ID())


# --- Run tests and write to directories
if not os.path.exists("./in"):
    os.makedirs("in")

if not os.path.exists("./out"):
    os.makedirs("out")


for i in range(1, num_tests + 1):
    for ID in teams:
        w.add_team(ID)

    for ID in initial_players:
        w_new_player(ID)

    for j in range(0, num_commands):
        execute_test_command(random.choice(test_commands))

    w.write(f'./in/input{i}.in', f'./out/output{i}.out')
    w.clear()

    players = initial_players.copy()
    removed_players = []
    teams = initial_teams.copy()
    team_players = {ID: [] for ID in teams}

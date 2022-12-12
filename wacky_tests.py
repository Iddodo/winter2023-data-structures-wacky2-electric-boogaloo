#!/usr/bin/env python3

from Wacky2Unit import Wacky2Unit
import random

# --- Custom variables for test generation --- #

num_players = 1
num_teams = 1
num_commands = 1
random_integer_upper_bound = 300

# --- Player and team ID lists --- #

players = [i for i in range(1, num_players + 1)]
teams = [i for i in range(1, num_teams + 1)]
removed_players = []

team_players = {ID: [] for ID in teams}

# --- Functions to fetch relevant random values --- #
def random_team_ID():
    return random.choice(teams)

def random_player_ID(include_removed = False):
    if include_removed:
        return random.choice(players + removed_players)

    return random.choice(players)

def random_positive_integer():
    return random.randint(1, random_integer_upper_bound)

def new_team_ID():
    return max(teams) + 1

def new_player_ID():
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

def w_new_player(ID):
    r = [random_positive_integer() for i in range(0, 3)]
    team_ID = random_team_ID()
    w.add_player(ID, team_ID, 1, r[0], r[1], r[2], random.choice(True, False))

    team_players[team_ID].append(ID)

# --- Implementation of runtime commands ---- #
# Commands with actual function names assure non-invalid input,
# and prevents trivial failure (some failure may still occur).
def execute_test_command(cmd):

    if cmd == 'add_team':
        w.add_team(new_team_ID())

    if cmd == 'remove_team':
        team_ID = random_team_ID()
        w.remove_team(team_ID)

        for player_ID in team_players[team_ID]:
            players.remove(player_ID)
            removed_players.append(player_ID)

        teams.remove(team_ID)
        del team_players[team_ID]


    if cmd == 'add_player':
        w_new_player(new_player_ID())

    if cmd == 'play_match':
        w.play_match(random_team_ID(), random_team_ID())

    # Allow player IDs
    if cmd == 'num_played_games_for_player':
        w.num_played_games_for_player(
            random_player_id(include_removed = true))

    # TODO: also test for removed players
    if cmd == 'add_player_cards':
        w.add_player_cards(random_player_ID(), random_positive_integer())

    if cmd == 'get_player_cards':
        w.get_player_cards(
            random_player_id(include_removed = true))

    if cmd == 'get_team_points':
        w.get_team_points(random_team_ID())

    # TODO: problematic function, do more tests
    if cmd == 'get_ith_pointless_ability':
        w.get_ith_pointless_ability(random.randint(0, len(teams)))

    if cmd == 'get_partial_spirit':
        w.get_partial_spirit(random_player_ID())

    if cmd == 'buy_team':
        w.buy_team(random_team_ID(), random_team_ID())

for ID in teams:
    w.add_team(ID)

for ID in players:
    r = [random_positive_integer() for i in range(0, 3)]
    w.add_player(ID, random_team_ID(), 1, r[0], r[1], r[2], random.choice(True, False))


for i in range(0, num_commands):
    execute_test_command(random.choice(test_commands))

w.write('wacky.in', wacky.out)
w.clear()

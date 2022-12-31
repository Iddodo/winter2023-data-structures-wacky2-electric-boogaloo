#! import numpy as np
#/usr/bin/env python3
from dataclasses import dataclass
import numpy
import functools


class Team:
    def __init__(self, ID, points, players):
        self.ID = ID
        self.points = points
        self.players = players

    def player_exists(self, playerId):
        for player in self.players:
            if player.ID == playerId:
                return True

        return False

    def ability(self):
        res = 0
        for player in self.players:
            res += player.ability

        return res

    def play_match_ability(self):
        return self.ability() + self.points

    def spirit_permutation(self, playerId=None):
        upper_bound = len(self.players) if not (playerId and self.player_exists(playerId)) else ([i.ID for i in self.players].index(
            playerId) + 1)
        res = numpy.array([0,1,2,3,4])
        for player in self.players[:upper_bound]:
            res = res[player.spirit]

        return res

    # Called strength in t_permutation
    # sympy permutations start from zero, therefore Python 'ai' is cpp 'a[i] + 1'
    def spirit(self):

        s = 0
        perm = self.spirit_permutation()

        for i, ai in enumerate(perm):
            s += (i * 1) * ((ai + 1) + 1)

        return s

    def increment_player_games(self):
        for player in self.players:
            player.games_played += 1

    def has_goalkeeper(self):
        for player in self.players:
            if player.is_goalkeeper:
                return True
        return False


@dataclass
class Player:
    ID: int
    games_played: int
    team: Team
    cards: int
    is_goalkeeper: bool
    ability: int
    spirit: numpy.ndarray


class Wacky2Unit:
    def __init__(self):
        self.expected = []
        self.input = []
        self.teams = {}
        self.players = {}
        self.removed_players = {}

    def __add_input(self, input_list):
        self.input.append(' '.join([str(x) for x in input_list]))

    def __add_expected(self, keycode, status, more=None):
        self.expected.append(str(keycode) + ': ' + str(status) + ('' if more == None else ', ' + str(more)))

    def __add_expected_raw(self, text):
        self.expected.append(text)

    def write(self, in_file, out_file):
        f_test = open(in_file, 'w')
        f_expected = open(out_file, 'w')

        f_test.write('\n'.join(self.input))
        f_expected.write('\n'.join(self.expected) + '\n')

        f_test.close()
        f_expected.close()

    def clear(self):
        self.expected = []
        self.input = []
        self.teams = {}
        self.players = {}
        self.removed_players = {}

    # ----------------------------------------

    def __permutation_string(self, perm):
        return ','.join(str(e + 1) for e in list(perm))

    def __is_valid_permutation(self, perm):
        if len(list(perm)) != 5: return False

        histogram = {e: 0 for e in range(0,5)}

        for e in perm:
            histogram[e] += 1

        for e in range(0,5):
            if histogram[e] != 1:
                return False

        return True


    def add_team(self, teamId):
        self.__add_input(['add_team', teamId])

        if teamId <= 0:
            self.__add_expected('add_team', 'INVALID_INPUT')
            return

        if teamId in self.teams:
            self.__add_expected('add_team', 'FAILURE')
            return

        self.teams[teamId] = Team(ID=teamId, points=0, players=[])
        self.__add_expected('add_team', 'SUCCESS')

    def remove_team(self, teamId):
        self.__add_input(['remove_team', teamId])

        if teamId <= 0:
            self.__add_expected('remove_team', 'INVALID_INPUT')
            return

        if teamId not in self.teams:
            self.__add_expected('remove_team', 'FAILURE')
            return

        # Remove players from tournament, add to removed players
        for player in self.teams[teamId].players:
            del self.players[player.ID]
            self.removed_players[player.ID] = player

        del self.teams[teamId]
        self.__add_expected('remove_team', 'SUCCESS')

    def add_player(self, playerId, teamId, spirit, gamesPlayed, ability, cards, goalKeeper):
        spirit = numpy.array([e - 1 for e in spirit])
        self.__add_input(
            ['add_player', playerId, teamId, self.__permutation_string(spirit), gamesPlayed, ability, cards, 'true' if goalKeeper else 'false'])
        invalid_input = False

        if playerId <= 0 or teamId <= 0:
            self.__add_expected('add_player', 'INVALID_INPUT')
            return

        if not self.__is_valid_permutation(spirit):
            self.__add_expected('add_player', 'INVALID_INPUT')
            return

        if gamesPlayed < 0 or cards < 0:
            self.__add_expected('add_player', 'INVALID_INPUT')
            return

        if (playerId in self.players) or (playerId in self.removed_players) or (teamId not in self.teams):
            self.__add_expected('add_player', 'FAILURE')
            return

        team = self.teams[teamId]

        self.players[playerId] = Player(
            ID=playerId,
            games_played=gamesPlayed,
            team=team,
            cards=cards,
            is_goalkeeper=goalKeeper,
            ability=ability,
            spirit=spirit
        )

        team.players.append(self.players[playerId])

        self.__add_expected('add_player', 'SUCCESS')

    def play_match(self, teamId1, teamId2):
        self.__add_input(['play_match', teamId1, teamId2])

        if (teamId1 <= 0) or (teamId2 <= 0) or (teamId1 == teamId2):
            self.__add_expected('play_match', 'INVALID_INPUT')
            return

        if (teamId1 not in self.teams) or (teamId2 not in self.teams):
            self.__add_expected('play_match', 'FAILURE')
            return

        team1 = self.teams[teamId1]
        team2 = self.teams[teamId2]

        if not (team1.has_goalkeeper() and team2.has_goalkeeper()):
            self.__add_expected('play_match', 'FAILURE')
            return

        TIE, ABILITY1, SPIRIT1, ABILITY2, SPIRIT2 = range(0, 5)
        winner = None
        winner_code = TIE

        if team1.play_match_ability() != team2.play_match_ability():
            winner_code = ABILITY1 if team1.play_match_ability() > team2.play_match_ability() else ABILITY2
        else:
            str1 = team1.spirit()
            str2 = team2.spirit()

            if str1 != str2:
                winner_code = SPIRIT1 if str1 > str2 else SPIRIT2

        if winner_code in [ABILITY1, SPIRIT1]:
            team1.points += 3
        elif winner_code in [ABILITY2, SPIRIT2]:
            team2.points += 3
        else:
            team1.points += 1
            team2.points += 1

        # Increment games_played for every player
        team1.increment_player_games()
        team2.increment_player_games()

        self.__add_expected('play_match', 'SUCCESS', winner_code)

    def num_played_games_for_player(self, playerId):
        func = 'num_played_games_for_player'
        self.__add_input([func, playerId])

        if playerId <= 0:
            self.__add_expected(func, 'INVALID_INPUT')
            return

        if playerId in self.players:
            self.__add_expected(func, 'SUCCESS', self.players[playerId].games_played)
            return

        if playerId in self.removed_players:
            self.__add_expected(func, 'SUCCESS', self.removed_players[playerId].games_played)
            return

        self.__add_expected(func, 'FAILURE')

    def add_player_cards(self, playerId, cards):
        func = 'add_player_cards'
        self.__add_input([func, playerId, cards])

        if playerId <= 0 or cards < 0:
            self.__add_expected(func, 'INVALID_INPUT')
            return

        if playerId not in self.players:
            self.__add_expected(func, 'FAILURE')
            return

        self.players[playerId].cards += cards

        self.__add_expected(func, 'SUCCESS')

    def get_player_cards(self, playerId):
        func = 'get_player_cards'
        self.__add_input([func, playerId])

        if playerId <= 0:
            self.__add_expected(func, 'INVALID_INPUT')
            return

        if playerId in self.players:
            self.__add_expected(func, 'SUCCESS', self.players[playerId].cards)
            return

        if playerId in self.removed_players:
            self.__add_expected(func, 'SUCCESS', self.removed_players[playerId].cards)
            return

        self.__add_expected(func, 'FAILURE')

    def get_team_points(self, teamId):
        func = 'get_team_points'
        self.__add_input([func, teamId])

        if teamId <= 0:
            self.__add_expected(func, 'INVALID_INPUT')
            return

        if teamId not in self.teams:
            self.__add_expected(func, 'FAILURE')
            return

        self.__add_expected(func, 'SUCCESS',
                            self.teams[teamId].points)

    def get_ith_pointless_ability(self, i):
        func = 'get_ith_pointless_ability'
        self.__add_input([func, i])

        if (i < 0) or (len(self.teams) == 0) or (len(self.teams) <= i):
            self.__add_expected(func, 'FAILURE')
            return

        teams_by_ability = [
            {
                'teamId': ID,
                'ability': self.teams[ID].ability()
            }
            for ID in self.teams
        ]

        def sort_dicts_by_ability(d1, d2):
            if d1['ability'] != d2['ability']:
                return -1 if d1['ability'] < d2['ability'] else 1

            return -1 if d1['teamId'] < d2['teamId'] else 1

        teams_by_ability.sort(key=functools.cmp_to_key(sort_dicts_by_ability))

        self.__add_expected(func, 'SUCCESS', teams_by_ability[i]['teamId'])

    def get_partial_spirit(self, playerId):
        func = 'get_partial_spirit'
        self.__add_input([func, playerId])

        if playerId <= 0:
            self.__add_expected(func, 'INVALID_INPUT')
            return

        if playerId not in self.players:
            self.__add_expected(func, 'FAILURE')
            return

        perm = self.players[playerId].team.spirit_permutation(playerId=playerId)

        self.__add_expected(func, 'SUCCESS', self.__permutation_string(perm))

    def buy_team(self, buyerId, boughtId):
        func = 'buy_team'
        self.__add_input([func, buyerId, boughtId])

        if (buyerId <= 0) or (boughtId <= 0) or (buyerId == boughtId):
            self.__add_expected(func, 'INVALID_INPUT')
            return

        if (buyerId not in self.teams) or (boughtId not in self.teams):
            self.__add_expected(func, 'FAILURE')
            return

        buyer = self.teams[buyerId]
        bought = self.teams[boughtId]

        # All players are being added according to their
        # original order in their corresponding team.
        #
        # buyerId.players are 'veterans' and therefore appear first
        # in the chronological order.
        buyer.players += bought.players
        buyer.points += bought.points

        # Update bought team player's 'team' prop
        for player in bought.players:
            player.team = buyer

        del self.teams[boughtId]

        self.__add_expected(func, 'SUCCESS')

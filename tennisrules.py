# This module defines classes for the entities one would expect to manipulate
# when working with a tennis match: match, players, set, game and point
#

SCORING_SYSTEM = {'0': 0, '15': 1, '30': 2, '40': 3, 'A': 4}

# Define match formats:

# WTA Grand Slam with Australian Open rules final set 'Super Tiebreak' (10 points to win) at 6-6
WTA_GRAND_SLAM_AUS = {'POINTS_IN_GAME': 4, 'POINTS_IN_TB': 7, 'GAMES_IN_SET': 6, 'SETS_TO_WIN': 2, 'LAST_SET_TB': True, 'LAST_TB_POINTS': 10}


# ATP Grand Slam with 5th set Tiebreak (Wimbledon, US Open)
ATP_GRAND_SLAM_TB = {'POINTS_IN_GAME': 4, 'POINTS_IN_TB': 7, 'GAMES_IN_SET': 6, 'SETS_TO_WIN': 3, 'LAST_SET_TB': True, 'LAST_TB_POINTS': 7}
# ATP Grand Slam with Australian Open rules final set 'Super Tiebreak' (10 points to win) at 6-6
ATP_GRAND_SLAM_AUS = {'POINTS_IN_GAME': 4, 'POINTS_IN_TB': 7, 'GAMES_IN_SET': 6, 'SETS_TO_WIN': 3, 'LAST_SET_TB': True, 'LAST_TB_POINTS': 10}
# ATP Grand Slam with no 5th set tiebreak (French Open)
ATP_GRAND_SLAM_NOTB = {'POINTS_IN_GAME': 4, 'POINTS_IN_TB': 7, 'GAMES_IN_SET': 6, 'SETS_TO_WIN': 3, 'LAST_SET_TB': False}

STANDARD_ATP_WTA = {'POINTS_IN_GAME': 4, 'POINTS_IN_TB': 7, 'GAMES_IN_SET': 6, 'SETS_TO_WIN': 2, 'LAST_SET_TB': True, 'LAST_TB_POINTS': 7}



class Player:
    def __init__(self, firstname, lastname):
        self.First = firstname
        self.Last = lastname

    def full_name(self):
        return (self.First + ' ' + self.Last)

class Point:
    def __init__(self, score):
        self.Score = score
    
    def PrintScore(self):
        print(self.Score)

def gamewinner(game):
    winner = 0
    lastpoint = game.Score[-1]
    if game.TB == True:
        if int(lastpoint.Score[0]) > int(lastpoint.Score[1]):
            winner = 0
        else:
            winner = 1
    else:
        if SCORING_SYSTEM[lastpoint.Score[0]] > SCORING_SYSTEM[lastpoint.Score[1]]:
            winner = 0
        else:
            winner = 1
    
    return winner 


class Game:
    def __init__(self, score, tb = False):
        self.Score = score
        self.TB = tb
        self.Winner = gamewinner(self)

    def Point(self, number):
        if number < 1 or number > len(self.Score):
            raise Exception('Index out of bound')
        return self.Score[number-1]
    
    def PrintScore(self):
        print([point.Score for point in self.Score])



class Set:
    def __init__(self, number, score):
        self.Number = number
        self.Score = score
        self.Winner = None

    def Game(self, number):
        if number < 1 or number > len(self.Score):
            raise Exception('Index out of bound')
        return self.Score[number-1]
    
    def AddGame(self, game_score):
        self.Score = self.Score + [game_score]

    def FindWinner(self):
        winner = 0
        lastgame = self.Score[-1]

        if lastgame.Winner == 0:
            winner = 0
        elif lastgame.Winner == 1:
            winner = 1
        else:
            raise Exception('Set winner cannot be identified')

        self.Winner = winner

    def PrintScore(self):
        print('Set ' + str(self.Number) + ':')
        for game in self.Score:
            game.PrintScore()
        print('\n')




class Match:
    def __init__(self, player1, player2, rules=STANDARD_ATP_WTA, info={}):
        self.Score = []
        self.Players = [player1, player2]
        self.Rules = rules # support for different match lengths (slam, 5th set TB, 5th set 'super TB', etc...)
        self.Info = info # Dict. Possible fields are 'DATE', 'CIRCUIT', 'MATCH_TYPE', 'TOURNAMENT', 'COURT_TYPE', 'ROUND'

    def PrintPlayers(self):
        return (self.Players[0].full_name() + ' - ' + self.Players[1].full_name())

    def Set(self, number):
        if number < 1 or number > len(self.Score):
            raise Exception('Index out of bound')
        return self.Score[number-1]

    def AddSet(self, set_score):
        self.Score = self.Score + set_score

    def PrintScore(self):
        for set_ in self.Score:
            set_.PrintScore()


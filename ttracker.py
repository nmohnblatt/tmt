import tennisrules as tennis

def trackmatch(match):
    set_tally = [0, 0]
    game_tally = [0, 0]
    to_win = [[], []]

    end_of_set = [0]

    max_points = match.Rules['SETS_TO_WIN']*match.Rules['GAMES_IN_SET']*match.Rules['POINTS_IN_GAME']

    for set_ in match.Score:
        for game in set_.Score:
            for point in game.Score:
                point_tally = [score_to_int(point.Score[i], game.TB) for i in [0, 1]]
                for i in [0,1]:
                    to_win[i].append(max_points-points_until_victory(i, match.Rules, set_, game, set_tally, game_tally, point_tally))
            game_tally[game.Winner] += 1
        set_tally[set_.Winner] += 1
        end_of_set.append(len(to_win[0]))
        game_tally = [0, 0]

    return to_win[0], to_win[1], end_of_set

def points_until_victory(player, rules, set_, game, set_tally, game_tally, point_tally):
    opponent = (player+1)%2
 
    ## 1) Find the number of sets required
    sets_objective = rules['SETS_TO_WIN']

    ## 2) Find the number of full games needed to win the current set
    games_objective = max(rules['GAMES_IN_SET'], game_tally[opponent]+2) # default value
   
    
    if set_.Number == sets_objective*2-1 and rules['LAST_SET_TB'] == False:
        # If this set does not allow tiebreaks, mark tiebreak objective as 0
        # (i.e. keep the default value for 'games_objective')
        tb_objective = 0
    else:
        # Else (if the set allows tiebreaks), check whether a tiebreak is needed
        if game_tally[opponent] == rules['GAMES_IN_SET'] and not game.TB:
            # If the opponent has scored the maximum number of games, and that the current game is not a tiebreak
            tb_objective = 1
            games_objective = rules['GAMES_IN_SET']
        else:
            tb_objective = 0

    if game.TB:
        games_objective = rules['GAMES_IN_SET']+1


    ## 3) Find the number of points needed to win the current game
    # If the game is a last set tiebreak
    tb_points = rules['POINTS_IN_TB']
    if game.TB and set_.Number == sets_objective*2-1:
        tb_points = rules['LAST_TB_POINTS']
        points_objective = max(tb_points, point_tally[opponent]+2)
    # Else, if the game is a regular tiebreak
    elif game.TB and set_.Number != sets_objective*2-1:
        points_objective = max(tb_points, point_tally[opponent]+2)
    # Else (when the game is a regular game)
    else:
        points_objective = max(rules['POINTS_IN_GAME'], point_tally[opponent]+2) # default value

    
    future_sets_needed = sets_objective - set_tally[player] - 1
    future_games_needed = games_objective - game_tally[player] - 1
    out = future_sets_needed*rules['GAMES_IN_SET']*rules['POINTS_IN_GAME']+future_games_needed*rules['POINTS_IN_GAME'] + tb_objective*tb_points + points_objective-point_tally[player]
    return out


def score_to_int(score, tb):
    if tb:
        return int(score)
    else:
        return tennis.SCORING_SYSTEM[score]
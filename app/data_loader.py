from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import sqlite3
from .predict import predictGame

connect = sqlite3.connect('nba_betting.db')

gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable= '2025-26')
games = gamefinder.get_data_frames()[0]

games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])

games.to_sql('games_raw', connect, if_exists='replace', index=False)

df = pd.read_sql("SELECT * FROM games_raw", connect)
# This is gonna do an infinite loop bc 'getGames' in utils calls this function too
def load_team_stats(home_team, away_team):
  game_data = getGames(home_team, away_team)
  if game_data:
    data = np.array([game_data])
    probability = predictGame(data)
    return probability


connect.close()




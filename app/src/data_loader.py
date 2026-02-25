from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import sqlite3

connect = sqlite3.connect('nba_betting.db')

gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable= '2025-26')
games = gamefinder.get_data_frames()[0]

games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])

games.to_sql('games_raw', connect, if_exists='replace', index=False)

df = pd.read_sql("SELECT * FROM games_raw", connect)
print(df)

connect.close()




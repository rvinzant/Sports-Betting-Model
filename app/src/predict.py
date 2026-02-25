import sqlite3
import pandas as pd

connect = sqlite3.connect('nba_betting.db')
df = pd.read_sql("SELECT * FROM games_raw", connect)


home_games = df[df['MATCHUP'].str.contains('vs.')].copy()
away_games = df[df['MATCHUP'].str.contains('@')].copy()

model_df = pd.merge(home_games,away_games, on='GAME_ID', suffixes=('_HOME','_AWAY'))

print(model_df)
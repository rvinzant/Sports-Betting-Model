from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import numpy as np
import sqlite3

# gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable= '2025-26')
# games = gamefinder.get_data_frames()[0]

# games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])

# games.to_sql('games_raw', connect, if_exists='replace', index=False)

# df = pd.read_sql("SELECT * FROM games_raw", connect)
def load_team_stats(team):
  with sqlite3.connect('nba_betting.db') as connect:
    recent_games_prompt = f"""
          SELECT AVG(PTS) AS avg_points,
                AVG(PLUS_MINUS) AS avg_plus_minus 
          FROM (
              SELECT PTS, PLUS_MINUS
              FROM games_raw
              WHERE TEAM_NAME = '{team}'
              ORDER BY GAME_DATE DESC
              LIMIT 10
          ) AS recent_games;
        """
    return pd.read_sql(recent_games_prompt, connect)

  # recent = df[df['TEAM_NAME'] == team].sort_values('GAME_DATE', ascending=False).head(5)
  # return recent[['PTS', 'PLUS_MINUS']].mean()

  # game_data = getPreviousGameData(home_team, away_team)
  # if game_data:
  #   data = np.array([game_data])
  #   probability = predictGame(data)
  #   return probability
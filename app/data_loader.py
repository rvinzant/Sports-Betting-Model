from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import numpy as np
import sqlite3

# gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable= '2025-26')
# games = gamefinder.get_data_frames()[0]

# games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])

# games.to_sql('games_raw', connect, if_exists='replace', index=False)

# df = pd.read_sql("SELECT * FROM games_raw", connect)
DB_PATH = 'nba_betting.db'

def update_nba_data():
    """Fetches the latest games from the NBA API and saves them to the database."""
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # 1. Pull the most recent games for the current season [cite: 35]
        # Using a date_from filter ensures we only get recent data
        gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable='2025-26')
        games = gamefinder.get_data_frames()[0]

        # 2. Clean data: Ensure date is in the correct format
        games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])

        # 3. Use a staging table to avoid duplicates (UPSERT logic)
        games.to_sql('staging_table', conn, if_exists='replace', index=False)

        # Only insert rows where the GAME_ID and TEAM_ID combination is new
        conn.execute("""
            INSERT OR IGNORE INTO games_raw 
            SELECT * FROM staging_table
        """)
        
        conn.commit()
        print("Database updated with latest NBA games.")

    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        conn.close()

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
  
def main():
   update_nba_data()

if __name__ == "__main__":
   main()
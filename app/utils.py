from .logging_config import logger

teams = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets",
    "Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers",
    "Dallas Mavericks","Denver Nuggets","Detroit Pistons",
    "Golden State Warriors","Houston Rockets","Indiana Pacers",
    "LA Clippers","Los Angeles Lakers","Memphis Grizzlies",
    "Miami Heat","Milwaukee Bucks","Minnesota Timberwolves",
    "New Orleans Pelicans","New York Knicks","Oklahoma City Thunder",
    "Orlando Magic","Philadelphia 76ers","Phoenix Suns",
    "Portland Trail Blazers","Sacramento Kings","San Antonio Spurs",
    "Toronto Raptors","Utah Jazz","Washington Wizards"]


#------------------------------
# Read files
def get_file_content(file_path):
    logger.debug(f"get_file_content function entered in utils.py for file: {file_path}")
    try:
        with open(file_path, 'r') as f:
            logger.debug(f"Successfully opened and read file: {file_path}")
            return f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return "File not found."
    except IOError as e:
        logger.warning(f"Error reading file: {e}")
        return "Error reading file."
    

#------------------------------
def getPreviousGameData(home_team, away_team):
    from .data_loader import load_team_stats

    home_stats = load_team_stats(home_team)
    away_stats = load_team_stats(away_team)
    if home_stats.empty or away_stats.empty:
        logger.error("Could not find stats for one of the teams.")
        return None
    home_last_5_pts = home_stats["avg_points"].iloc[0]
    away_last_5_pts = away_stats["avg_points"].iloc[0]
    plus_minus_home = home_stats["avg_plus_minus"].iloc[0]
    plus_minus_away = away_stats["avg_plus_minus"].iloc[0]
    print(f"Previous game data for {home_team} vs {away_team}: {home_last_5_pts}, {away_last_5_pts}, {plus_minus_home}, {plus_minus_away}")
    game_data = [home_last_5_pts, away_last_5_pts, plus_minus_home, plus_minus_away]
    logger.debug(f"Game data for {home_team} vs {away_team}: {game_data}")
    return game_data
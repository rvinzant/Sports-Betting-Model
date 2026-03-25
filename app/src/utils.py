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
def getGames():
    logger.debug("Games function entered in utils.py")
    # get all future games and add them to a list
    futureGames = [[]]
    logger.debug("Games function exited in utils.py")
    return futureGames
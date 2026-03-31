import os
import lightgbm as lgb
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "models", "nba_model.txt")
model = lgb.Booster(model_file=model_path)

# Format: [HOME_LAST_5_PTS, AWAY_LAST_5_PTS, PLUS_MINUS_HOME, PLUS_MINUS_AWAY]
# Example: Pacers (Home) vs Celtics (Away)
def predictGame(homeTeam, awayTeam):
    # TODO: get the data needed and predict based off that

    # array holds needed data
    tonight_data = np.array([[110.2, 112.5, 2.1, -1.2]])
    probability = model.predict(tonight_data)[0]

    return f"{probability:.2%} chance of Home Team winning."


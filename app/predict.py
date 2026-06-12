import os
import lightgbm as lgb
import numpy as np
from .utils import getPreviousGameData

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "models", "nba_model.txt")
model = lgb.Booster(model_file=model_path)

# Format: [HOME_LAST_5_PTS, AWAY_LAST_5_PTS, PLUS_MINUS_HOME, PLUS_MINUS_AWAY]
# Example: Pacers (Home) vs Celtics (Away)
def predictGame(homeTeam, awayTeam):
    tonight_data = np.array([getPreviousGameData(homeTeam, awayTeam)])

    if tonight_data is None:
        return "Prediction couldn't be made."
    print(f"predict.py - Data for prediction: {tonight_data}")

    probability = model.predict(tonight_data)[0]
    answer = ""
    if probability > 0.5:
        answer = f"{probability:.2%} chance of {homeTeam} winning."
    else:
        answer = f"{1 - probability:.2%} chance of {awayTeam} winning."

    return answer


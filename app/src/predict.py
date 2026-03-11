import lightgbm as lgb
import numpy as np
# from .train import getGameData

# 1. Load the model
model = lgb.Booster(model_file='nba_model.txt')

# 2. Prepare "Tonight's" data
# Format: [HOME_LAST_5_PTS, AWAY_LAST_5_PTS, PLUS_MINUS_HOME, PLUS_MINUS_AWAY]
# Example: Pacers (Home) vs Celtics (Away)
tonight_data = np.array([[118.2, 112.5, 3.1, -1.2]])

# 3. Predict
probability = model.predict(tonight_data)[0]

print(f"Prediction: {probability:.2%} chance of Home Team winning.")


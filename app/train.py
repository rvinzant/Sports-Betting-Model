import os
import pandas as pd
import sqlite3
import lightgbm as lgb
from sklearn.model_selection import train_test_split


def trainModel():
    # --- STEP 1: LOAD DATA FROM DATABASE ---
    connect = sqlite3.connect('nba_betting.db')

    # We need TEAM_ID to group games and GAME_DATE to ensure chronological order
    query = "SELECT GAME_ID, GAME_DATE, MATCHUP, TEAM_ID, WL, PTS, PLUS_MINUS FROM games_raw"
    df = pd.read_sql(query, connect)
    connect.close()

    # Ensure dates are proper objects and sorted
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values('GAME_DATE')

    # --- STEP 2: CREATE model_df (The "Pivoting" step) ---
    # Separate rows into Home and Away
    home_games = df[df['MATCHUP'].str.contains('vs.')].copy()
    away_games = df[df['MATCHUP'].str.contains('@')].copy()

    # Merge so one row = one game with Home and Away stats
    model_df = pd.merge(home_games, away_games, on='GAME_ID', suffixes=('_HOME', '_AWAY'))

    # --- STEP 3: FEATURE ENGINEERING (Rolling Averages) ---
    # Calculate the average points and plus_minus of the PREVIOUS 10 games for each team
    model_df['HOME_LAST_10_PTS'] = model_df.groupby('TEAM_ID_HOME')['PTS_HOME'].transform(lambda x: x.rolling(10).mean().shift(1))
    model_df['AWAY_LAST_10_PTS'] = model_df.groupby('TEAM_ID_AWAY')['PTS_AWAY'].transform(lambda x: x.rolling(10).mean().shift(1))
    model_df['HOME_LAST_10_PM'] = model_df.groupby('TEAM_ID_HOME')['PLUS_MINUS_HOME'].transform(lambda x: x.rolling(10).mean().shift(1))
    model_df['AWAY_LAST_10_PM'] = model_df.groupby('TEAM_ID_AWAY')['PLUS_MINUS_AWAY'].transform(lambda x: x.rolling(10).mean().shift(1))

    # Drop games where we don't have enough history (the first 10 games in dataset)
    model_df = model_df.dropna(subset=['HOME_LAST_10_PTS', 'AWAY_LAST_10_PTS', 'HOME_LAST_10_PM', 'AWAY_LAST_10_PM'])

    # --- STEP 4: PREPARE LIGHTGBM DATA ---
    features = ['HOME_LAST_10_PTS', 'AWAY_LAST_10_PTS', 'HOME_LAST_10_PM', 'AWAY_LAST_10_PM']
    X = model_df[features]
    # Convert 'W' to 1 and 'L' to 0
    y = model_df['WL_HOME'].apply(lambda x: 1 if x == 'W' else 0)

    # Split data (shuffle=False keeps the most recent games for testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Create LightGBM datasets
    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    # --- STEP 5: TRAINING ---
    params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'learning_rate': 0.01,
        'num_leaves': 20,
        'verbose': -1
    }

    model = lgb.train(params, train_data, valid_sets=[test_data])

    print("Model Training Complete!")

    # --- STEP 6: QUICK EVALUATION ---
    preds = model.predict(X_test)
    # Convert probabilities to 1 or 0
    binary_preds = [1 if p > 0.5 else 0 for p in preds]
    accuracy = (binary_preds == y_test).mean()
    print(f"Test Set Accuracy: {accuracy:.2%}")
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(model_dir, exist_ok=True)
    model.save_model(os.path.join(model_dir, "nba_model.txt"))


# To train model running by running file
if __name__ == "__main__":
    trainModel()
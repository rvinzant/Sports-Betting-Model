# Sports-Betting-Model

sports_betting_project/
├── data/                      # Data storage (not tracked by git)
│   ├── raw/                   # Unprocessed scraped/API data
│   ├── processed/             # Cleaned data ready for ML
│   └── external/              # Odds data, rosters, etc.
├── models/                    # Saved trained model files (.pkl, .h5, etc.)
├── notebooks/                 # Jupyter notebooks for EDA and testing
├── src/                       # Core source code
│   ├── __init__.py
│   ├── config.py              # Centralized configuration (API keys, paths)
│   ├── data_loader.py         # Scripts to fetch data from APIs/Scrapers
│   ├── preprocessing.py       # Cleaning and feature engineering
│   ├── train.py               # Model training and hyperparameter tuning
│   ├── predict.py             # Inference script for upcoming games
│   └── utils.py               # Helper functions (logging, math)
├── tests/                     # Unit and integration tests
├── requirements.txt           # Python dependencies
├── .gitignore                 # Exclude /data, /models, and venv
└── README.md                  # Project overview and setup instructions

# Tech Stack
- Python 3.x
- Flask
- Flask-Login
- SQLAlchemy
- Bootstrap 5 ?

## Install Dependencies
```bash
pip install -r requirements.txt
```
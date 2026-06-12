# Sports-Betting-Model


## Admin: 
### username 'admin', password 'admin123'
- Change log level 
- Check logs on webpage
- Update the DB with more recent games
- Force backup DB and Logs
- Delete backups older than 20 days
- Force create a new log file


# Tech Stack
- Python 3.x
- Flask
- Flask-Login
- SQLAlchemy
- Bootstrap 5  


# Guide to run model (Mac)
- Open Terminal (Press Command + Spacebar, type Terminal, and press Enter)
- Run cd ~/Desktop
- Run git clone https://github.com/rvinzant/Sports-Betting-Model
- Run cd Sports-Betting-Model
- Run sh start.sh
- Look for something like this: (http://127.0.0.1:8000)
- Copy and paste that into a browser
- Hit the Betting Model button in the top left
- Enter the information of the game you want to predict.


# Guide to run model (Windows)
- Open Command Prompt 
- Run cd %userprofile%\Desktop
- Run git clone https://github.com/rvinzant/Sports-Betting-Model
- Run cd Sports-Betting-Model
- Run start.bat
- Look for something like this: http://127.0.0.1:8000
- Copy and paste that into a browser
- Hit the Betting Model in the top left
- Enter the information of the game you want to predict.

## Install Dependencies
```bash
pip install -r requirements.txt
```

## Run using docker
```bash
docker build -t betting-model .
docker run -p 5050:5050 betting-model
```



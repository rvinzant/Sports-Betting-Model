import os
import logging

# Function to get or set the saved log level in config.txt
def savedLevel(type=str, value=str):
    logger.info(f"savedLevel function in logging_config.py called with type: {type}, value: {value}")
    idx = -1
    level = None
    data = []
    with open("config.txt", 'r') as f:
        data = f.readlines()
        for line in data:
            idx += 1
            if line.startswith("log-level:"):
                level = line.split(": ")[1].strip()
                break
        f.close()
    # Recieve the log level
    if type == "GET":
        if not level:
            logger.warning("No log level found in config, defaulting to INFO")
            return logging.INFO  # Default log level
        logger.info(f"Log level set to {level} from config")
        if level == "DEBUG":
            return logging.DEBUG
        elif level == "INFO":
            return logging.INFO
        elif level == "WARNING":
            return logging.WARNING
        elif level == "ERROR":
            return logging.ERROR
        elif level == "CRITICAL":
            return logging.CRITICAL         
    else:
        # Set the log level
        logger.info(f"Setting log level to {value} in config")
        with open("config.txt", 'w') as f:
            if idx != -1:
                data[idx] = f"log-level: {value}\n"
            f.writelines(data)
            f.close()
        return

# Create a logs folder in the root of the project
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
log_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "betting_model.log")

logger = logging.getLogger("BettingLogger")
logger.setLevel(logging.DEBUG)

# Create handlers and configure them
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARN)

file_handler = logging.FileHandler(log_file_path)
level = savedLevel("GET", None)
if level is None:
    level = logging.INFO
file_handler.setLevel(level)

# Create formatter and add it to handlers
formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Remove all previous handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Remove default logs 
logging.getLogger('werkzeug').handlers = []
log = logging.getLogger('werkzeug')
log.setLevel(logging.FATAL)

# Add new handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)
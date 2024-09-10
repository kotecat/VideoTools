import os
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)
dotenv_path = ".env"

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logger.info("Config loaded!")
else:
    logger.error("Prepare .env file")
    exit()


class Config:
    API_ID = str(os.getenv("API_ID"))
    API_HASH = str(os.getenv("API_HASH"))
    BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
    ADMIN_IDS = set(map(lambda id: int(id.strip()), os.getenv("ADMIN_IDS").split(",")))
    
    TIMEOUT = 1000
    MAX_THREADS = 1  # NOT WORK
    
    DIR_MEDIA = "m"
    FFMPEG_BIN = "ffmpeg"
    
    DEFAULT_BIT_RATE_V = 10
    DEFAULT_FPS = 1
    DEFAULT_BIT_RATE_A = 10

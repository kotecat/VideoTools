from pyrogram import Client, enums
import platform
import logging

from src.config import Config


logger = logging.getLogger(__name__)

__phone = Config.PHONE_NUMBER or None
__bot_token = (Config.BOT_TOKEN or None) if __phone is None else None

if __phone is None and __bot_token is None:
    logger.error("Set please phone number or bot token in .env")
    exit()


bot = Client(
    "VideoBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=__bot_token,
    phone_number=__phone,
    app_version="v0.0.1",
    device_model="pyrofork",
    system_version=f"{platform.system()} {platform.release()}",
    lang_code="ru",
    workers=50,
    parse_mode=enums.ParseMode.HTML
)

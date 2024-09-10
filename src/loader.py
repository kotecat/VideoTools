from pyrogram import Client, enums
import platform

from src.config import Config


bot = Client(
    "VideoBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    app_version="v0.0.1",
    device_model="pyrofork",
    system_version=f"{platform.system()} {platform.release()}",
    lang_code="ru",
    workers=50,
    parse_mode=enums.ParseMode.HTML
)

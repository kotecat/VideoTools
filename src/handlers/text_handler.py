from pyrogram import Client
from pyrogram.types import Message
from pyrogram.filters import private, user

from src.loader import bot
from src.config import Config


@bot.on_message(private & user(list(Config.ADMIN_IDS)))
async def text_handler(client: Client, message: Message):
    await message.reply("<b>Send a video!</b>")


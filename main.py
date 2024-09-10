import logging
logging.basicConfig(level=logging.INFO)

from src.loader import bot
import src.handlers


if __name__ == "__main__":
    bot.run()

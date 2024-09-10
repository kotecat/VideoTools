import logging
logging.basicConfig(level=logging.INFO)

from src.loader import bot
import src.handlers


def main():
    bot.run()


if __name__ == "__main__":
    main()

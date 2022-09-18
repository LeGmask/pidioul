#!/usr/bin/env python3
import logging

from src.config import settings
from src.pidioul import Pidioul

bot = Pidioul()

try:
	bot.run(settings.discord.token, root_logger=True)
finally:
	logging.log(logging.INFO, "Shutting down...")

#!/usr/bin/env python3
import logging
import discord

from config import settings
from src.pidioul import Pidioul

bot = Pidioul(command_prefix='/', intents=discord.Intents.all())

try:
	bot.run(settings.discord.token, root_logger=True)
finally:
	logging.log(logging.INFO, "Shutting down...")

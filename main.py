#!/usr/bin/env python3
from typing import Literal, Optional

import discord
from discord.ext import commands

from config import settings
from src.pidioul import Pidioul

bot = Pidioul(command_prefix='/', intents=discord.Intents.all())

try:
	bot.run(settings.discord.token, root_logger=True)
finally:
	print('EXITING GRACEFULLY')

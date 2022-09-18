import logging
import os

import discord
from discord.ext import commands
from dynaconf import Dynaconf

from src.config import settings
from src.database import Database


class Pidioul(commands.Bot):
	def __init__(self) -> None:
		super().__init__(command_prefix='/', intents=discord.Intents.all())
		self.config = settings
		self.database = Database(self.config)

	async def load_cogs(self) -> None:
		for file in os.listdir('cogs'):
			if file.endswith('.py'):
				await self.load_extension(f'cogs.{file[:-3]}', package=__package__)

	async def setup_hook(self) -> None:
		await self.load_cogs()

	async def on_ready(self):
		logger = logging.getLogger(__name__)
		logger.log(logging.INFO, f"Logged in as {self.user.name} (ID: {self.user.id}) on {len(self.guilds)} guilds")

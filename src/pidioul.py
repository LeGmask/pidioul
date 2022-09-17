import logging
from discord.ext import commands

from cogs.loader import Cogs


class Pidioul(commands.Bot):
	async def setup_hook(self) -> None:
		await Cogs(self).load()

	async def on_ready(self):
		logger = logging.getLogger(self.__class__.__name__)
		logger.log(logging.INFO, f"Logged in as {self.user.name} (ID: {self.user.id}) on {len(self.guilds)} guilds")

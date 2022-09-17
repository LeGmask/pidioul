import os

import discord.ext.commands


class Cogs:
	def __init__(self, bot: discord.ext.commands.Bot) -> None:
		self.bot = bot

	async def load(self) -> None:
		for file in os.listdir('cogs'):
			if file.endswith('.py') and file != 'loader.py':
				await self.bot.load_extension(f'cogs.{file[:-3]}', package=__package__)

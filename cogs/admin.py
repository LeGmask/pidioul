import logging
from typing import Optional, Literal

import discord
from discord import app_commands
from discord.ext import commands

from src.config import settings
from src.game import Game
from src.models.runtimeConfig import RuntimeConfig
from src.pidioul import Pidioul


class AdminCog(commands.GroupCog, name="admin"):
	def __init__(self, bot: Pidioul) -> None:
		self.bot = bot
		super().__init__()

		self.logger = logging.getLogger(__name__)
		self.logger.log(logging.INFO, f"Loaded {self.__class__.__name__}")

	@commands.command()
	@commands.guild_only()
	@commands.is_owner()
	async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object],
				   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
		"""Syncs the slash commands with the bot's commands."""
		if not guilds:
			if spec == "~":
				synced = await ctx.bot.tree.sync(guild=ctx.guild)
			elif spec == "*":
				ctx.bot.tree.copy_global_to(guild=ctx.guild)
				synced = await ctx.bot.tree.sync(guild=ctx.guild)
			elif spec == "^":
				ctx.bot.tree.clear_commands(guild=ctx.guild)
				await ctx.bot.tree.sync(guild=ctx.guild)
				synced = []
			else:
				synced = await ctx.bot.tree.sync()

			await ctx.send(
				f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
			)
			self.logger.log(logging.INFO,
							f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
			return

		ret = 0
		for guild in guilds:
			try:
				await ctx.bot.tree.sync(guild=guild)
			except discord.HTTPException:
				pass
			else:
				ret += 1

		await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
		self.logger.log(logging.INFO, f"Synced the tree to {ret}/{len(guilds)}.")

	@app_commands.command(name="setup_channel")
	@app_commands.checks.has_permissions(administrator=True)
	async def setup_channel(self, interaction: discord.Interaction) -> None:
		"""
		Set up the channel for the game.
		Create a message with instructions and a thread for the game.

		:param interaction:
		:return:
		"""
		RuntimeConfig.upsert('guild_id', interaction.guild.id)
		RuntimeConfig.upsert('channel_id', interaction.channel.id)
		await interaction.response.send_message(self.bot.config.chess.game_message, ephemeral=False)
		message = await interaction.original_response()
		thread = await message.create_thread(name="Play here")
		RuntimeConfig.upsert('thread', thread.id)

		game = Game(settings)
		game.new_board()
		game.save_board()

		board = await message.channel.send(file=game.get_discord_file())
		RuntimeConfig.upsert('message_board', board.id)


async def setup(bot: Pidioul) -> None:
	await bot.add_cog(AdminCog(bot))

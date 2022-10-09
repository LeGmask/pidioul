import logging
from datetime import datetime
from typing import Optional, Literal

import discord
from discord import app_commands
from discord.ext import commands

from src.config import settings
from src.game import Game
from src.models.color import Color
from src.models.piece import Piece
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

		RuntimeConfig.upsert('nextWhitePlay', datetime.now().replace(hour=12, minute=0, second=0,
																	 microsecond=0).timestamp())
		board = await message.channel.send(file=game.get_discord_file())
		RuntimeConfig.upsert('message_board', board.id)

	@app_commands.command(name="setup_color_role")
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(color="The color you want to assign a role to.",
						   role="The role you want to assign to the color.")
	async def setup_color_role(self, interaction: discord.Interaction, color: Literal['white', 'black'],
							   role: discord.Role) -> None:
		"""
		Set up the role that belong to a color.

		:param interaction:
		:param color:
		:param role:
		:return:
		"""
		color = Color.get(Color.name == color)
		color.role = role.id
		color.save()

		await interaction.response.send_message(f"Role {role.mention} assigned to color {color.name}.", ephemeral=True)

	@app_commands.command(name="setup_piece_role")
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(piece="The piece you want to assign a role to.",
						   role="The role you want to assign to the piece.")
	async def setup_piece_role(self, interaction: discord.Interaction, piece: Literal[
		"rook_l", "knigh_l", "bishop_l", "queen", "king", "bishop_r", "knight_r", "rook_r", "pawn"],
							   role: discord.Role) -> None:
		"""
		Set up the role that belong to a color.

		:param piece:
		:param interaction:
		:param role:
		:return:
		"""
		piece = Piece.get(Piece.name == piece)
		piece.role = role.id
		piece.save()

		await interaction.response.send_message(f"Role {role.mention} assigned to {piece.name}.", ephemeral=True)


async def setup(bot: Pidioul) -> None:
	await bot.add_cog(AdminCog(bot))

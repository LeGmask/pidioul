import logging
from datetime import datetime

import chess
import discord
from discord import app_commands
from discord.ext import commands

from src.config import settings
from src.game import Game
from src.models.runtimeConfig import RuntimeConfig
from src.pidioul import Pidioul
from src.utils import get_user_possible_pieces, get_user_color
from src.views.play import PlayView


def check_if_valid_thread(interaction: discord.Interaction) -> bool:
	"""Checks if the interaction is in the good thread."""
	return interaction.channel.id == int(RuntimeConfig.get_key("thread").value)


async def check_if_playable(interaction: discord.Interaction) -> bool:
	"""Checks if current user can play."""
	game = Game(settings)
	next_white_play = RuntimeConfig.get_key_or_default("nextWhitePlay", 0)

	if datetime.now().timestamp() >= float(next_white_play):
		return True

	await interaction.response.send_message("There's no more move for today :p", ephemeral=True)
	return False


class Chess(commands.Cog):
	def __init__(self, bot: Pidioul) -> None:
		self.logger = logging.getLogger(__name__)
		self.game = Game(bot.config)
		self.bot = bot
		self.logger.log(logging.INFO, f"Loaded {self.__class__.__name__}")

	@app_commands.command(name="play")
	@app_commands.check(check_if_valid_thread)
	@app_commands.check(check_if_playable)
	async def play(self, interaction: discord.Interaction) -> None:
		"""
		Play a move of your choice for your piece(s).
		:param interaction:
		:return:
		"""
		# check if the color is the same as the user
		user_color = get_user_color(interaction.user)
		if user_color is None:
			await interaction.response.send_message("You don't have a color assigned, you can't play", ephemeral=True)
			return
		if self.game.board.turn != (get_user_color(interaction.user).id == 1):
			await interaction.response.send_message("It's not your turn.", ephemeral=True)
			return

		pieces = get_user_possible_pieces(interaction.user)

		# if the user has no pieces, return
		if not pieces:
			await interaction.response.send_message("You don't have any piece to play with", ephemeral=True)
			return

		# if the user has only one piece, gameboard show possible moves
		if len(pieces) == 1:
			message = 'Select the move you want to play',
			png = self.game.get_discord_file(
				squares=chess.SquareSet(
					[move.to_square for move in self.game.get_possible_moves_from(pieces[0].position)],
				),
			)
		else:
			message = 'You have multiple pieces (highlighted in blue), select the one you want to play with'
			png = self.game.get_discord_file(fill=dict.fromkeys([piece.position for piece in pieces], "#8fbcbb"))

		await interaction.response.send_message(message, ephemeral=True, view=PlayView(self.game, pieces), files=[png])


async def setup(bot):
	await bot.add_cog(Chess(bot))

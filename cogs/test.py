import logging

import chess
import discord
from discord import app_commands
from discord.ext import commands

from src.game import Game
from src.pidioul import Pidioul
from src.utils import get_user_possible_pieces
from src.views.play import PlayView


class Test(commands.Cog):
	def __init__(self, bot: Pidioul) -> None:
		self.logger = logging.getLogger(__name__)
		self.game = Game(bot.config)
		self.bot = bot
		self.logger.log(logging.INFO, f"Loaded {self.__class__.__name__}")

	@app_commands.command(name="test")
	async def test(self, interaction: discord.Interaction) -> None:
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

		# await interaction.response.send_message(content="test", files=[gameboard], ephemeral=True)
		await interaction.response.send_message(message, ephemeral=True, view=PlayView(self.game, pieces), files=[png])


async def setup(bot):
	await bot.add_cog(Test(bot))

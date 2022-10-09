from typing import List

import chess
import discord
from discord import ButtonStyle
from discord.ui import View, Button, Select

from src.game import Game
from src.models.gameboard import GameBoard
from src.models.runtimeConfig import RuntimeConfig


class ActionButton(Button):
	def __init__(self, game: Game, move: chess.Move):
		self.game = game
		self.action = move

		message = chess.square_name(move.to_square)
		if move.promotion:
			message += f" and promote to {chess.piece_name(move.promotion)}"
		super().__init__(label=message, style=ButtonStyle.primary)

	async def callback(self, interaction: discord.Interaction):
		self.game.move(self.action)

		# if self.action.to_square in range(56 * self.game.board.turn, 8 + 56 * self.game.board.turn):
		# 	await interaction.response.edit_message(
		# 		content=f"This move require a promotion. Please select a piece to promote to.",
		# 		view=PromotionView(self.game, self.action))
		# else:
		await interaction.response.edit_message(content=f"playing {self.action}",
												attachments=[self.game.get_discord_file()], view=None)

		await interaction.channel.send(f"{interaction.user.mention} playing {self.action}")

		# update the gameboard svg
		message = await interaction.channel.parent.fetch_message(int(RuntimeConfig.get_key('message_board').value))
		await message.edit(attachments=[self.game.get_discord_file()])
		self.view.stop()


class PieceSelect(Select):
	def __init__(self, pieces: List[GameBoard]):
		super().__init__(placeholder="Select your piece",
						 options=[discord.SelectOption(label=f"{piece.piece.name}, {chess.square_name(piece.position)}",
													   value=str(id)) for
								  id, piece in enumerate(pieces)])

	async def callback(self, interaction: discord.Interaction):
		self.view.piece = self.view.pieces[int(self.values[0])]
		self.view.update_view(force_update=True)

		png = self.view.game.get_discord_file(
			fill={self.view.piece.position: "#d08770"},
			squares=chess.SquareSet(
				[move.to_square for move in self.view.game.get_possible_moves_from(self.view.piece.position)],
			),
		)
		await interaction.response.edit_message(content='Select the move you want to play', view=self.view,
												attachments=[png])


class NextPageButton(Button):
	async def callback(self, interaction: discord.Interaction):
		self.view.page += 1
		self.view.update_view()
		await interaction.response.edit_message(view=self.view)


class PreviousPageButton(Button):
	async def callback(self, interaction: discord.Interaction):
		self.view.page -= 1
		self.view.update_view()
		await interaction.response.edit_message(view=self.view)


class PlayView(View):
	def __init__(self, game: Game, pieces: List[GameBoard]):
		super().__init__()

		self.number_of_buttons = None
		self.pieces: None | List[GameBoard] = pieces
		self.piece: None | GameBoard = None
		self.game = game

		self.moves = []
		self.page = 0

		if len(self.pieces) > 1:
			self.add_item(PieceSelect(self.pieces))
		else:
			self.pieces = self.pieces[0]
			self.update_view()

	def insert_page_control(self):
		self.add_item(Button(label=" ", style=ButtonStyle.grey, row=4, disabled=True))
		self.add_item(PreviousPageButton(label="Previous", style=ButtonStyle.blurple, row=4, disabled=self.page == 0))
		self.add_item(
			Button(label=f"{self.page + 1}/{len(self.moves) // self.number_of_buttons}", style=ButtonStyle.grey, row=4,
				   disabled=True))
		self.add_item(NextPageButton(label="Next", style=ButtonStyle.blurple, row=4,
									 disabled=len(self.moves) // self.number_of_buttons == self.page + 1))
		self.add_item(Button(label=" ", style=ButtonStyle.grey, row=4, disabled=True))

	def update_view(self, force_update=False):
		items = filter(lambda item: not isinstance(item, PieceSelect), self.children)
		for item in items:
			self.remove_item(item)

		if not self.moves or force_update:  # populate the moves if it's empty
			self.moves = self.game.get_possible_moves_from(self.piece.position)

		if len(self.moves) > 25 - (5 * len(self.children)):
			self.number_of_buttons = 20 - (5 * len(self.children))
			self.insert_page_control()
		else:
			self.number_of_buttons = len(self.moves)

		for i in range(self.page * self.number_of_buttons, self.number_of_buttons + self.page * self.number_of_buttons):
			self.add_item(ActionButton(self.game, self.moves[i]))

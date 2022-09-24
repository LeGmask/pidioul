from typing import List

import chess
import discord
from discord.ui import View, Button, Select

from src.game import Game
from src.models.gameboard import GameBoard


class ActionButton(Button):
	def __init__(self, game: Game, move: chess.Move):
		self.game = game
		self.action = move
		super().__init__(label=str(move)[2:])

	async def callback(self, interaction: discord.Interaction):
		self.game.move(self.action)

		await interaction.response.edit_message(content=f"playing {self.action}",
												attachments=[self.game.get_discord_file()], view=None)
		self.view.stop()


class PieceSelect(Select):
	def __init__(self, pieces: List[GameBoard]):
		super().__init__(placeholder="Select your piece",
						 options=[discord.SelectOption(label=f"{piece.piece.name}, {piece.position}", value=str(id)) for
								  id, piece in enumerate(pieces)])

	async def callback(self, interaction: discord.Interaction):
		self.view.piece = self.view.pieces[int(self.values[0])]
		self.view.init_move_selection()

		png = self.view.game.get_discord_file(
			squares=chess.SquareSet(
				[move.to_square for move in self.view.game.get_possible_moves_from(self.view.piece.position)],
			),
		)
		await interaction.response.edit_message(content='Select the move you want to play', view=self.view,
												attachments=[png])


class PlayView(View):
	def __init__(self, game: Game, pieces: List[GameBoard]):
		super().__init__()

		self.pieces: None | List[GameBoard] = pieces
		self.piece: None | GameBoard = None
		self.game = game

		if len(self.pieces) > 1:
			self.add_item(PieceSelect(self.pieces))
		else:
			self.pieces = self.pieces[0]

	# for action in self.game.get_possible_moves_from(self.pieces.position):
	# 	self.add_item(ActionButton(self.game, action))

	def init_move_selection(self):
		for action in self.game.get_possible_moves_from(self.piece.position):
			self.add_item(ActionButton(self.game, action))

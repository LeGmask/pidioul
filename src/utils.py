from typing import Union, List

import discord

from src.models.color import Color
from src.models.gameboard import GameBoard
from src.models.piece import Piece


def get_user_possible_pieces(user: Union[discord.User, discord.Member]) -> List[GameBoard]:
	user_roles = [role.id for role in user.roles]

	try:
		color = [color for color in Color.select() if color.role in user_roles][0]
		user_piece = [piece for piece in Piece.select() if piece.role in user_roles][0]
	except IndexError:
		return []

	return [piece for piece in GameBoard.select().where(GameBoard.piece == user_piece, GameBoard.color == color)]

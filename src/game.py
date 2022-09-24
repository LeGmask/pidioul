import io
import os

import chess
import chess.pgn
import chess.svg
import discord
from cairosvg import svg2png
from dynaconf import Dynaconf

from src.models.color import Color
from src.models.gameboard import GameBoard
from src.models.piece import Piece


class Game:
	def __init__(self, config: Dynaconf) -> None:
		self.board: chess.Board | None = None
		self.state: None | Color = None
		self.config = config.chess
		self.load_board()

	def load_board(self) -> None:
		if os.path.isfile(self.config.save_file):
			# Load the board moves by reading the pgn file
			game = chess.pgn.read_game(open(self.config.save_file))

			# create a new board
			self.board = game.board()

			# restore the board by replaying the moves
			for move in game.mainline_moves():
				self.board.push(move)
		else:
			self.new_board()

		self.update_state()

	def new_board(self) -> None:
		self.board = chess.Board()
		self.save_board()

		# initialize the database
		GameBoard.delete().execute()  # delete all the records to start a new game
		for color in Color.select():
			for piece in Piece.select():
				# in case of a pawn, we add it to the board 8 times since there are 8 pawns
				if piece.name == 'pawn':
					for i in range(8):
						GameBoard.create(
							piece=piece,
							color=color,
							position=i + (8 if color.color == 'white' else 48),
						)
				else:
					GameBoard.create(piece=piece, color=color, position=((color.id - 1) * 56) + piece.position)

	def save_board(self) -> None:
		with open(self.config.save_file, "w") as pgn_file:
			pgn = chess.pgn.Game.from_board(self.board)
			exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)

			# create a pgn string from the board and write it to the file
			pgn_file.write(pgn.accept(exporter))

	def get_png(self, **kwargs) -> bytes:
		# if there is a last move, highlight it
		if self.board.move_stack:
			kwargs['lastmove'] = self.board.move_stack[-1]

		return svg2png(bytestring=chess.svg.board(self.board, size=800, **kwargs))

	def get_discord_file(self, **kwargs) -> discord.File:
		return discord.File(io.BytesIO(self.get_png(**kwargs)), filename='board.png')

	def get_possible_moves_from(self, square: chess.Square) -> list[chess.Move]:
		return list(self.board.generate_legal_moves(from_mask=chess.BB_SQUARES[square]))

	def move(self, move: chess.Move) -> None:
		if not self.board.is_legal(move):
			raise InvalidMoveException('Illegal move')

		# If the move is a capture, remove the piece from the board
		if self.board.is_capture(move):
			captured_piece = GameBoard.get(GameBoard.position == move.to_square)
			captured_piece.position = None
			captured_piece.save()

		# If the move is an en passant, remove the piece from the board
		if self.board.is_en_passant(move):
			captured_piece = GameBoard.get(GameBoard.position == move.to_square + (8 if self.board.turn else -8))
			captured_piece.position = None
			captured_piece.save()

		# If the move is a castling, move the rook
		if self.board.is_castling(move):
			rook = GameBoard.get(
				GameBoard.position == (move.to_square + 1 if move.to_square > move.from_square else move.to_square - 2))
			rook.position = move.to_square - 1
			rook.save()

		# Move
		self.board.push(move)

		# Do the move in the database
		piece = GameBoard.get(GameBoard.position == move.from_square)
		piece.position = move.to_square
		piece.save()

		self.save_board()

	def is_color(self, color: Color) -> bool:
		return self.board.turn == (color.color == 'white')

	def update_state(self):
		result = self.board.result()
		if self.board.result() != '*':
			if result == '1-0':
				self.state = Color.select().where(Color.color == 'white').get()
			elif result == '0-1':
				self.state = Color.select().where(Color.color == 'black').get()

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.save_board()


class InvalidMoveException(Exception):
	pass

# def get_possible_moves(self, piece) -> list:
# 	return self.board.legal_moves
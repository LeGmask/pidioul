from src.models.color import Color
from src.models.piece import Piece


def seed():
	Piece.create(name='rook_l', position=0)
	Piece.create(name='knigh_l', position=1)
	Piece.create(name='bishop_l', position=2)
	Piece.create(name='queen', position=3)
	Piece.create(name='king', position=4)
	Piece.create(name='bishop_r', position=5)
	Piece.create(name='knight_r', position=6)
	Piece.create(name='rook_r', position=7)

	Piece.create(name='pawn', position=8)

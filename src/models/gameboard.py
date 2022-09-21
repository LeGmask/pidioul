import peewee

from src.database import BaseModel
from src.models.color import Color
from src.models.piece import Piece


class GameBoard(BaseModel):
	id = peewee.PrimaryKeyField()
	piece = peewee.ForeignKeyField(Piece, backref='piece')
	color = peewee.ForeignKeyField(Color, backref='color')
	position = peewee.IntegerField(null=True)

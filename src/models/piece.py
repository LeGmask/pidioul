import peewee

from src.database import BaseModel
from src.models.color import Color


class Piece(BaseModel):
	id = peewee.PrimaryKeyField()
	name = peewee.CharField()
	role = peewee.BigIntegerField(null=True, default=None)
	position = peewee.IntegerField(null=True)

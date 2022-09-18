import peewee

from src.database import BaseModel


class Game(BaseModel):
	name = peewee.CharField()


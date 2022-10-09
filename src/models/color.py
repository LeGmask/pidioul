import peewee

from src.database import BaseModel


class Color(BaseModel):
	id = peewee.PrimaryKeyField()
	name = peewee.CharField(unique=True)
	role = peewee.IntegerField(null=True, default=None)

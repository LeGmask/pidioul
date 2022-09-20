import peewee

from src.database import BaseModel


class Color(BaseModel):
	id = peewee.PrimaryKeyField()
	color = peewee.CharField(unique=True)
	role = peewee.CharField(null=True, default=None)

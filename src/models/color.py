import peewee

from src.database import BaseModel


class Color(BaseModel):
	id = peewee.PrimaryKeyField()
	color = peewee.CharField(unique=True)
	role = peewee.IntegerField(null=True, default=None)

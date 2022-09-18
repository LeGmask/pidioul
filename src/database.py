import sqlite3

import peewee
from peewee_migrate import Router

from src.config import settings


class Database:
	db = peewee.SqliteDatabase(settings.database.path)

	def __init__(self, config) -> None:
		self.config = config.database
		self.cursor = self.db.cursor()


class BaseModel(peewee.Model):
	class Meta:
		database = Database.db

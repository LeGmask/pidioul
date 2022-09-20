import logging
import os
import sys

import discord.utils
import peewee
from peewee_migrate import Router

from src.config import settings
from src.database import Database, BaseModel

discord.utils.setup_logging()  # Setup same logging as discord.py


class SeedHistory(BaseModel):
	"""Seed history model."""
	id = peewee.PrimaryKeyField()
	name = peewee.CharField(unique=True)
	seeded_at = peewee.DateTimeField(default=peewee.datetime.datetime.now)


def seed(logger: logging.Logger) -> None:
	"""Seed the database with initial values."""
	seeded = [previousSeed.name for previousSeed in SeedHistory.select()]
	for file in os.listdir('seeders'):
		if file.endswith('.py') and file[:-3] not in seeded:
			logger.log(logging.INFO, f"Seeding {file}")
			seeder = __import__(f'seeders.{file[:-3]}', fromlist=['seed'])
			seeder.seed()
			SeedHistory.create(name=file[:-3])


db = Database(settings)
router = Router(db.db, migrate_dir='migrations', logger=logging.getLogger('migration.py'))  # migration engine
db.db.create_tables([SeedHistory])  # create seed history table if it doesn't exist

match sys.argv[1]:
	case 'new':
		router.create(sys.argv[2])
	case 'up':
		router.run()
	case 'down':
		if router.done:
			router.rollback(router.done[-1])
		else:
			router.logger.warning('No migrations to rollback')
	case 'seed':
		seed(router.logger)
	case 'reset':
		os.remove(settings.database.path)
	case _:
		router.logger.error('Invalid command')

import logging
import sys

import discord.utils
from peewee_migrate import Router

from src.config import settings
from src.database import Database

discord.utils.setup_logging()  # Setup same logging as discord.py

db = Database(settings)
router = Router(db.db, migrate_dir='migrations', logger=logging)  # migration engine

match sys.argv[1]:
	case 'new':
		router.create(sys.argv[2])
	case 'up':
		router.run()
	case 'down':
		if (router.done):
			router.rollback(router.done[-1])
		else:
			router.logger.warning('No migrations to rollback')

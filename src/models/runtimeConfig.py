import peewee

from src.database import BaseModel


class RuntimeConfig(BaseModel):
	id = peewee.PrimaryKeyField()
	key = peewee.CharField(unique=True)
	value = peewee.CharField()

	@staticmethod
	def get_key(key):
		return RuntimeConfig.select().where(RuntimeConfig.key == key).get()

	@staticmethod
	def get_key_or_default(key, default):
		try:
			return RuntimeConfig.get_key(key).value
		except peewee.DoesNotExist:
			return default

	@staticmethod
	def upsert(key, value):
		RuntimeConfig.insert(key=key, value=value).on_conflict(conflict_target=RuntimeConfig.key,
															   preserve=(RuntimeConfig.id, RuntimeConfig.key),
															   update={RuntimeConfig.value: value}).execute()

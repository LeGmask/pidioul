from src.models.color import Color


def seed():
	Color.create(name='white')
	Color.create(name='black')

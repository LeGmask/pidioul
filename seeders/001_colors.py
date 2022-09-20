from src.models.color import Color


def seed():
	Color.create(color='white')
	Color.create(color='black')

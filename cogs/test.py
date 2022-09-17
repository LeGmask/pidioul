import logging

from discord.ext import commands


class Test(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.logger = logging.getLogger(__name__)

		self.bot = bot
		self.logger.log(logging.WARN, f"Loaded {self.__class__.__name__}")

	@commands.command()
	async def test(self, ctx):
		await ctx.send('test')


async def setup(bot):
	await bot.add_cog(Test(bot))

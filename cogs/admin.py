from typing import Optional, Literal

import discord
from discord import app_commands
from discord.ext import commands


class AdminCog(commands.GroupCog, name="admin"):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		super().__init__()

	@commands.command()
	@commands.guild_only()
	@commands.is_owner()
	async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object],
				   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
		"""Syncs the slash commands with the bot's commands."""
		if not guilds:
			if spec == "~":
				synced = await ctx.bot.tree.sync(guild=ctx.guild)
			elif spec == "*":
				ctx.bot.tree.copy_global_to(guild=ctx.guild)
				synced = await ctx.bot.tree.sync(guild=ctx.guild)
			elif spec == "^":
				ctx.bot.tree.clear_commands(guild=ctx.guild)
				await ctx.bot.tree.sync(guild=ctx.guild)
				synced = []
			else:
				synced = await ctx.bot.tree.sync()

			await ctx.send(
				f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
			)
			return

		ret = 0
		for guild in guilds:
			try:
				await ctx.bot.tree.sync(guild=guild)
			except discord.HTTPException:
				pass
			else:
				ret += 1

		await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


	@app_commands.command(name="sub-2")
	async def my_sub_command_2(self, interaction: discord.Interaction) -> None:
		""" /parent sub-2 """
		await interaction.response.send_message("Hello from sub command 2", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(AdminCog(bot))

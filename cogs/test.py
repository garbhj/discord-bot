import discord
from discord.ext import commands


class Test(commands.Cog, name="test"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="test", description="Testing.")
    async def test(self, context: commands.Context) -> None:
        await context.reply("hello!")


async def setup(bot) -> None:
    await bot.add_cog(Test(bot))
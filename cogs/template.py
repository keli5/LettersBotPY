from discord.ext import commands
import discord


def __init__(self, bot):
    self.bot = bot


class cogname(commands.Cog):

    @commands.command()
    async def command(self, ctx):
        ''' Docstring here '''


def setup(bot):
    bot.add_cog(cogname(bot))

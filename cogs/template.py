from discord.ext import commands
import discord



class cogname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def command(self, ctx):
        """ Docstring here """


def setup(bot):
    bot.add_cog(cogname(bot))

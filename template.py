from discord.ext import commands
import discord


class cogname(commands.Cog):

    @commands.command()
    async def command(self, ctx):
        ''' Docstring here '''


def setup(bot):
    bot.add_cog(cogname(bot))
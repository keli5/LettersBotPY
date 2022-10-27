from discord.ext import commands


class cogname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def command(self, ctx):
        """ Docstring here """


async def setup(bot):
    await bot.add_cog(cogname(bot))

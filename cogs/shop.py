from discord.ext import commands


class Shop(commands.Cog):
    # TODO: Add shop cog to load list when this is in working order.
    # Here goes nothing.
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def command(self, ctx):
        """ Docstring here """


def setup(bot):
    bot.add_cog(Shop(bot))

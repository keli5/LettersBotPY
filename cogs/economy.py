from discord.ext import commands
import discord


class Economy(commands.Cog):
    """ Commands for the LettersBot "economy" """
    def __init__(self, bot):
        self.bot = bot
        self.currency = "֏"


    @commands.command()
    async def balance(self, ctx, victim: discord.User = None):
        """ View your balance or someone else's. """
        await ctx.send(self.currency)


def setup(bot):
    bot.add_cog(Economy(bot))

from discord.ext import commands
import discord
import random
import math
from classes.dbmodels import LBUser
from utility.funcs import db_for_user


class Economy(commands.Cog):
    """ Commands for the LettersBot "economy" """
    def __init__(self, bot):
        self.bot = bot
        self.cur = "֏"

    @commands.command()
    async def balance(self, ctx, user: discord.User = None):
        """ View your balance or someone else's. """
        user = user or ctx.author
        bal = await db_for_user(user.id, True)
        bal = bal.balance
        balembed = discord.Embed(
            title=f"{user} has {self.cur}{bal}!",
            description=f"Get more money with {self.bot.command_prefix}guess.",
            color=discord.Color.green()
        )
        await ctx.send(embed=balembed)

    @commands.command()
    async def guess(self, ctx, guess: int = 50):
        """ Play a guessing game for a chance to earn some money. """
        user = await db_for_user(ctx.author.id, True)
        userbal = user.balance
        value = random.randint(0, 100)
        earnings = 1000 if guess == value else round(50 / abs(value - guess) * 4, 2)
        gembed = discord.Embed(
            title=f"{self.cur} Guessing Game {self.cur}",
            color=discord.Color.green()
        )
        gembed.add_field(name="Your guess", value=guess)
        gembed.add_field(name="Actual number", value=value)
        if guess == value:
            gembed.add_field(name="JACKPOT!", value=f"You earned {self.cur}1,000!", inline=False)
            gembed.color = discord.Color.magenta()
        else:
            gembed.add_field(name="Earnings", value=f"You earned {self.cur}{earnings}.")
        await LBUser.filter(id=ctx.author.id).update(balance=userbal + earnings)  # tortoise why
        await ctx.send(embed=gembed)


def setup(bot):
    bot.add_cog(Economy(bot))

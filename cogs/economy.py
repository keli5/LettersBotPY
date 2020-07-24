from discord.ext import commands
import discord
import random
import asyncio
from classes.dbmodels import LBUser
from utility.funcs import db_for_user
from discord.ext.commands.cooldowns import BucketType


class Economy(commands.Cog):
    """ Commands for the LettersBot "economy" """
    def __init__(self, bot):
        self.bot = bot
        self.cur = "֏"

    @commands.command(aliases=["bal"])
    async def balance(self, ctx, user: discord.User = None):
        """ View your balance or someone else's. """
        user = user or ctx.author
        bal = await db_for_user(user.id, True)
        bal = bal.balance
        formatted = "{:.2f}".format(bal)  # What is this doing? Couldn't tell you
        balembed = discord.Embed(
            title=f"{user} has {self.cur}{formatted}!",
            description=f"Get more money with {self.bot.command_prefix}guess.",
            color=discord.Color.green()
        )
        await ctx.send(embed=balembed)

    @commands.command()
    @commands.cooldown(1, 45, BucketType.user)
    async def wheel(self, ctx, wager: float):
        """ Spin the wheel. Will you triple your wager, or lose it all? 45 second cooldown. """
        userdb = await db_for_user(ctx.author.id, True)
        if userdb.balance <= 0 or userdb.balance <= wager:
            await ctx.send("You can't afford that!")
            return
        wheelembed = discord.Embed(
            title="Spin the Wheel!"
        )
        wheelembed.color = discord.Color.magenta()
        msg = await ctx.send(embed=wheelembed)
        wheelembed.description = "Spinning..."
        await msg.edit(embed=wheelembed)
        multiplier = 1
        await asyncio.sleep(random.randint(10, 30)/10)
        multiplier = round(random.randint(-300, 300) / 100, 2)
        wheelembed.title = f"You won {multiplier}x your bet."
        winnings = round(wager * multiplier, 2)
        gl = ""
        if winnings > 0:
            gl = "earned"
            wheelembed.color = discord.Color.green()
        elif winnings < 0:
            gl = "lost"
            wheelembed.color = discord.Color.red()
        else:
            gl = "got"
            wheelembed.color = discord.Color.darker_grey()
        wheelembed.description = f"You {gl} {self.cur}{winnings}."
        await msg.edit(embed=wheelembed)
        if userdb.balance + winnings <= 0:
            await LBUser.filter(id=ctx.author.id).update(balance=0)
        else:
            await LBUser.filter(id=ctx.author.id).update(balance=userdb.balance + winnings)

    @commands.command()
    @commands.cooldown(1, 30, BucketType.user)
    async def guess(self, ctx, guess: int):
        """ Play a guessing game for a chance to earn some money. 30 sec cooldown. """
        if guess > 100 or guess < 0:
            return await ctx.send('Guess may not be below 0 or above 100.')
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
        await LBUser.filter(id=ctx.author.id).update(balance=userbal + float(earnings))  # tortoise why
        await ctx.send(embed=gembed)

    @commands.command()
    async def pay(self, ctx, user: discord.User, amount: float):
        """ Pay someone some of your money. """
        famount = "{:.2f}".format(round(amount, 2))
        if amount <= 0 or famount == "0.00":
            return await ctx.send('Amount may not be below or equal to 0.')
        mybal = await db_for_user(ctx.author.id, True)
        mybal = mybal.balance
        userbal = await db_for_user(user.id, True)
        userbal = userbal.balance
        if amount > mybal:
            return await ctx.send("You can't afford to pay that much!")
        await LBUser.filter(id=ctx.author.id).update(balance=mybal - amount)
        await LBUser.filter(id=user.id).update(balance=userbal + amount)
        famount = "{:.2f}".format(round(amount, 2))
        payembed = discord.Embed(
            title="Transaction complete!",
            description=f"{ctx.author} sent {self.cur}{famount} to {user}.",
            color=discord.Color.green()
        )
        theyget = "{:.2f}".format(round(userbal + amount, 2))
        youlose = "{:.2f}".format(round(mybal - amount, 2))
        payembed.add_field(name=f"{user}'s new balance", value=f"{self.cur}{theyget}")
        payembed.add_field(name=f"{ctx.author}'s new balance", value=f"{self.cur}{youlose}")
        await ctx.send(embed=payembed)


def setup(bot):
    bot.add_cog(Economy(bot))

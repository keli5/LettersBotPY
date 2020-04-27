from discord.ext import commands
import discord


class Utility_Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        ''' Show the bot's ping. '''
        await ctx.send(f"Ponged in **{round(bot.latency * 1000, 2)}**ms.")


def setup(bot):
    bot.add_cog(Utility_Commands(bot))
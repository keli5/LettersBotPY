from discord.ext import commands


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joinvc(self, ctx):
        if ctx.author.voice:
            if ctx.author.voice.channel:
                await ctx.author.voice.channel.connect()
                await ctx.send(f"Connected to {ctx.author.voice.channel.name}")
        else:
            await ctx.send("You are not in a voice channel.")

    


def setup(bot):
    bot.add_cog(Voice(bot))

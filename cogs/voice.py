from discord.ext import commands
voicestates = {}


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joinvc(self, ctx):
        if ctx.author.voice:
            if ctx.author.voice.channel:
                voicestate = await ctx.author.voice.channel.connect()
                await ctx.send(f"Connected to {ctx.author.voice.channel.name}")
                voicestates[ctx.guild.id] = voicestate
        else:
            await ctx.send("You are not in a voice channel.")

    @commands.command(aliases=["disconnect", "dc"])
    async def leavevc(self, ctx):
        botmember = ctx.guild.get_member(ctx.bot.user.id)
        if ctx.author.voice and botmember.voice:
            if ctx.author.voice.channel is botmember.voice.channel:
                await voicestates[ctx.guild.id].disconnect()
                await ctx.send(f"Disconnected from {ctx.author.voice.channel.name}")
                voicestates[ctx.guild.id] = None
            else:
                await ctx.send("You are not in the same voice channel as the bot.")
        else:
            await ctx.send("You are not in a voice channel.")


def setup(bot):
    bot.add_cog(Voice(bot))

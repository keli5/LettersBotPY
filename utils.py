from discord.ext import commands
import discord


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        ''' Show the bot's ping. '''
        await ctx.send(f"Ponged in **{round(self.bot.latency * 1000, 2)}ms.**")

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        ''' Get somebody's avatar, or your own. '''
        victim = victim or ctx.author
        avatarembed = discord.Embed(
            title=f"Avatar of {str(victim)}",
            color=victim.color
        )
        avatarembed.set_image(url=victim.avatar_url)
        await ctx.send(embed=avatarembed)

    @commands.command()
    async def userinfo(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        uiembed = discord.Embed(
            title=f"User info about {str(user)}",
            color=user.color,
            description="Dates are in mm/dd/yy HH:MM:SS format, UTC"
        )
        uiembed.add_field( name="Joined guild at", value=user.joined_at.strftime("%m/%d/%Y %H:%M") + " UTC"
        )
        uiembed.set_thumbnail(url=str(user.avatar_url))
        uiembed.add_field(name="Nickname", value=user.nick or "No nickname")
        rolestring = ""
        nroles = []
        for role in user.roles: nroles.append(role.name)
        if len(nroles) > 4:
            rolestring = f"{', '.join(nroles[1:4])} and {len(nroles) - 4} more"
        else:
            rolestring = ", ".join(nroles[1:4])
        uiembed.add_field(name="Roles", value=rolestring, inline=len(nroles)<4)

        await ctx.send(embed=uiembed)

def setup(bot):
    bot.add_cog(Utility(bot))
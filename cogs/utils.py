from discord.ext import commands
import discord
import os
from classes.dbmodels import LBUser, LBGuild
modeltypes = {
    "users": LBUser,
    "guilds": LBGuild
}
valid_fields = ["id", "inventory", "canUseBot", "balance", "muteRole"]

class Utility(commands.Cog):
    ''' Quick utility commands that provide mostly information '''

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        ''' Show the bot's ping. '''
        await ctx.send(f"Ponged in **{round(self.bot.latency * 1000, 2)}ms.**")

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        ''' Get somebody's avatar, or your own. '''
        victim = user or ctx.author
        avatarembed = discord.Embed(
            title=f"Avatar of {str(victim)}",
            color=victim.color
        )
        avatarembed.set_image(url=victim.avatar_url)
        await ctx.send(embed=avatarembed)

    @commands.command()
    async def userinfo(self, ctx, user: discord.Member = None):
        ''' Get some info about a user, or yourself. '''
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
        uiembed.add_field(name="ID", value=user.id)
        uiembed.add_field(name="Boosting?", value="Yes" if user.premium_since else "No")
        uiembed.add_field(name="On mobile", value="Yes" if user.is_on_mobile() else "No")
        await ctx.send(embed=uiembed)

    @commands.group(invoke_without_command=True)
    async def db(self, ctx):
        ''' Database manipulation commands. '''
        size = os.path.getsize("../lettersbot_data.sqlite3") / 1000
        await ctx.send(f"SQLite 3 database, {size} KB")

    @db.command()
    @commands.is_owner()
    async def set(self, ctx, model, id, item, value):
        ''' Set item of model id to value in the database. '''
        modelnm = model
        model = modeltypes[model] or LBUser
        id = id or ctx.author.id
        if not item in valid_fields:
            return await ctx.send(f'Invalid item {item}')
        await model.filter(id=id).update(**{item: value})

    @db.command()
    @commands.is_owner()
    async def get(self, ctx, model, id):
        ''' Get id from model in the database. '''
        modelnm = model
        model = modeltypes[model] or LBUser
        id = id or ctx.author.id
        result = await model.get(id=id)
        getembed = discord.Embed(
            title=f"{modelnm}.{id}"
        )
        for field in valid_fields:
            attr = ""
            try:
                atr = getattr(result, field)
                getembed.add_field(name=field, value=atr)
            except AttributeError:
                pass
        await ctx.send(embed=getembed)

def setup(bot):
    bot.add_cog(Utility(bot))
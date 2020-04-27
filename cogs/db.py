from discord.ext import commands
import discord
from classes.dbmodels import LBUser, LBGuild
modeltypes = {
    "users": LBUser,
    "guilds": LBGuild
}
valid_fields = ["id", "inventory", "canUseBot", "balance", "muteRole"]

class Database(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
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
    bot.add_cog(Database(bot))
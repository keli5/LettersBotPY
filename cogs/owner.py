from discord.ext import commands
import discord
from classes.dbmodels import LBUser, LBGuild
from utility.funcs import reload_markov
import os
import pkg_resources

modeltypes = {
    "users": LBUser,
    "guilds": LBGuild
}
valid_fields = ["id", "inventory", "canUseBot", "balance", "muteRole",
                "warnings", "banUntil", "joinMesg", "joinMesgChannel"]


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def botban(self, ctx, victim: discord.User):
        await LBUser.filter(id=victim.id).update(canUseBot=False)
        await ctx.send(f"Disallowed {victim} from using LettersBot.")

    @commands.command()
    @commands.is_owner()
    async def botunban(self, ctx, victim: discord.User):
        await LBUser.filter(id=victim.id).update(canUseBot=True)
        await ctx.send(f"Allowed {victim} to use LettersBot.")

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def db(self, ctx):
        ''' Database manipulation commands. '''
        tormver = pkg_resources.get_distribution("tortoise-orm").version
        size = os.path.getsize("../lettersbot_data.sqlite3") / 1000
        await ctx.send(f"SQLite 3 database, {size} KB\nUsing tortoise-orm {tormver}")

    @db.command()
    @commands.is_owner()
    async def set(self, ctx, model, id, item, value):
        ''' Set item of model id to value in the database. '''
        modelnm = model
        model = modeltypes[model] or LBUser
        id = id or ctx.author.id
        if item not in valid_fields:
            return await ctx.send(f'Invalid item {item}')
        await model.filter(id=id).update(**{item: value})
        await ctx.send(f"Set {modelnm}.{id}.{item} to {value}")

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
                attr = getattr(result, field)
                getembed.add_field(name=field, value=attr)
            except AttributeError:
                pass
        await ctx.send(embed=getembed)

    @commands.command(aliases=["reloadmkv"])
    @commands.is_owner()
    async def reloadmarkov(self, ctx):
        reload_markov()
        await ctx.send('Done')


def setup(bot):
    bot.add_cog(Owner(bot))

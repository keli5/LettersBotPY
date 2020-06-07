from discord.ext import commands
import discord
from classes.dbmodels import LBUser, LBGuild
from utility.funcs import reload_markov, call_markov, image_from_url
import os
import io
import random
import pkg_resources
import typing

modeltypes = {
    "users": LBUser,
    "guilds": LBGuild
}
valid_fields = ["id", "inventory", "canUseBot", "balance", "muteRole",
                "warnings", "banUntil", "joinMesg", "joinMesgChannel",
                "blacklisted", "disabledCommands"]


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def seedrng(self, ctx, seed):
        random.seed(a=seed, version=2)
        await ctx.message.add_reaction("✅")

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
        shm = os.path.getsize("lettersbot_data.sqlite3-shm")
        wal = os.path.getsize("lettersbot_data.sqlite3-wal")
        base = os.path.getsize("lettersbot_data.sqlite3")
        size = (shm + wal + base) / 1000
        await ctx.send(f"SQLite 3 database, {size} KB\nUsing tortoise-orm {tormver}")

    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, channel: typing.Union[discord.User, discord.TextChannel], markov: bool, *,
                 content: str = None):

        if markov:
            content = call_markov(900)
        await channel.send(content)
        if isinstance(channel, discord.User):
            await ctx.send(f"`Sent DM to {channel}`:\n{content}")
        else:
            await ctx.send(f"`Sent message in {channel.guild}/#{channel.name}`:\n{content}")

    @db.command(name="set")
    @commands.is_owner()
    async def set_db_item(self, ctx, model, id, item, value):
        ''' Set item of model id to value in the database. '''
        modelnm = model
        model = modeltypes[model] or LBUser
        id = id or ctx.author.id
        if item not in valid_fields:
            return await ctx.send(f'Invalid item {item}')
        await model.filter(id=id).update(**{item: value})
        await ctx.send(f"Set {modelnm}.{id}.{item} to {value}")

    @commands.command()
    @commands.is_owner()
    async def echo(self, ctx, *, content):
        await ctx.message.delete()
        await ctx.send(content)

    @db.command(name="get")
    @commands.is_owner()
    async def get_db_item(self, ctx, model, id):
        ''' Get id from model in the database. '''
        modelnm = model
        model = modeltypes[model] or LBUser
        id = id or ctx.author.id
        result = await model[id]
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

    @commands.command(aliases=["editpfp"])
    @commands.is_owner()
    async def setpfp(self, ctx, attachment=None):
        source = attachment or ctx.message.attachments[0].url or None
        out = io.BytesIO()
        image = await image_from_url(source)
        image.save(out, "png")
        out.seek(0)
        await ctx.bot.user.edit(avatar=out)

    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx, safe: bool = True):
        guildstring = ""
        for guild in ctx.bot.guilds:
            if safe:
                guildstring += f"{guild.name}\n"
            else:
                guildstring += f"{guild.name}, owned by {guild.owner.tag}\n"
                guildstring += f"ID {guild.id}\n"
            guildstring += f"{len(guild.members)} members\n"
            guildstring += "\n"  # padding
        await ctx.send(guildstring)


def setup(bot):
    bot.add_cog(Owner(bot))

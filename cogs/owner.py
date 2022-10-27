import io
import os
import random
import time
import typing

import discord
import humanize
import pkg_resources
from discord.ext import commands

from classes.dbmodels import GuildMarkovSettings, GuildShop, LBGuild, LBUser
from utility.funcs import (call_markov, image_from_url, paginate_list,
                           reload_markov, tally_users)

modeltypes = {
    "users": LBUser,
    "guilds": LBGuild,
    "markov": GuildMarkovSettings,
    "shop": GuildShop
}

valid_fields = ["id", "inventory", "canUseBot", "balance", "muteRole",
                "warnings", "banUntil", "joinMesg", "joinMesgChannel",
                "blacklisted", "disabledCommands", "items", "enabled"]


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
        size = (shm + wal + base)
        await ctx.send(f"SQLite 3 database, {humanize.naturalsize(size)}\nUsing tortoise-orm {tormver}")

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
        loadingmsg = await ctx.send(content="Reloading markov... `this may take a minute`")
        start = time.time()
        async with ctx.typing():
            reload_markov()
        end = time.time()
        await loadingmsg.delete()
        timed = round(end - start, 2)
        await ctx.send(f"Reloaded markov in {timed} seconds.")

    @commands.command()
    @commands.is_owner()
    async def stop(self, ctx):
        exit(0)

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
    async def guilds(self, ctx, page: int = 1, safe: bool = True):
        # guild.name, guild.id, guild.members, ctx.bot.guilds is amount of guilds, tally_users(ctx.bot)
        gembed = discord.Embed(
            title=f"Guilds (page {page}) ",
            color=discord.Color.blurple()
        )
        guilds = paginate_list(ctx.bot.guilds, 10, page)
        if len(guilds) == 0:
            return await ctx.send("That page doesn't exist!")
        for guild in guilds:
            if safe:
                gembed.add_field(name=guild.name, value=f"{guild.member_count} members")  # ??
            else:
                gembed.add_field(name=f"{guild.name} ({guild.id})",
                                 value=f"{guild.member_count} members, owned by {guild.owner}")

        gembed.set_footer(text=f"{len(ctx.bot.guilds)} guilds, {tally_users(ctx.bot)} unique users")

        await ctx.send(embed=gembed)


async def setup(bot):
    await bot.add_cog(Owner(bot))

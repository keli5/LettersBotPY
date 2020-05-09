import discord
from classes.dbmodels import LBGuild
import utility.funcs as utility
import tortoise.exceptions as te
from discord.ext import commands
import re
import random
corpus = open("corpus.txt", "a")


class LettersBot(commands.AutoShardedBot):  # when you going
    """ Welcome to the rewrite of LettersBot! """
    async def on_ready(self):
        utility.reload_markov()
        user_count = utility.tally_users(self)
        prefix = self.command_prefix
        await utility.setup()
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{user_count} users | {prefix}info"
            )
        )
        print("Ready!")

    async def on_message(self, message):
        if message.author.bot:
            return
        swregex = r"(^\W|d::|^```)"
        if len(message.content) > 8 and not re.match(swregex, message.content):
            corpus.write(message.content.lower() + "\n")

        if (self.user in message.mentions) or (random.random() < 0.1):
            await message.channel.send(utility.call_markov(900))

        user = await utility.db_for_user(message.author.id, True)
        try:  # todo: make this into a db_for_guild function
            await LBGuild.get(id=message.guild.id)
        except te.DoesNotExist:
            await LBGuild.create(
                id=message.guild.id,
                muteRole=0,
                joinMesg=None
            )
            print(f"Created entry for {message.guild}")

        if user.canUseBot:
            await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        excname = type(exception).__name__
        if isinstance(exception, commands.CommandNotFound):
            return

        errembed = discord.Embed(
            title=f"{excname} error",
            description=str(exception),
            color=0xAA0000
        )

        if excname != "CommandOnCooldown":  # dont need cooldowns logged
            print(f"{excname}: {exception}")
        errmsg = await ctx.send(embed=errembed)
        await errmsg.delete(delay=10)

    async def on_member_join(self, member):
        guild = member.guild
        guilddb = await LBGuild.filter(id=guild.id).first()
        joinmsg = getattr(guilddb, "joinMesg")
        chid = getattr(guilddb, "joinMesgChannel")
        joinmsgchannel = self.get_channel(chid) or guild.system_channel
        if (joinmsg is not None) and (joinmsgchannel is not None):
            await joinmsgchannel.send(f"{member.mention}\n{joinmsg}")

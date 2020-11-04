import discord
from classes.dbmodels import LBGuild
import utility.funcs as utility
import datetime
from discord.ext import commands, tasks
import re
import json
import difflib
import random
corpus = open("corpus.txt", "a")
started_at = datetime.datetime.now()


class LettersBot(commands.AutoShardedBot):  # when you going
    """ Welcome to the rewrite of LettersBot! """
    async def on_ready(self):
        config = json.loads(open("config.json").read())
        self.allowedLearningGuilds = config["markovGuilds"]
        self.queues = {}
        utility.reload_markov()
        for guild in self.guilds:
            self.queues[guild.id] = []
        await utility.setup()
        self.update_status.start()
        print("Ready!")

    @tasks.loop(minutes=5.0)
    async def update_status(self):
        try:
            user_count = utility.call_cmarkov(25)
        except Exception:
            user_count = "with you"

        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"{user_count} | {self.command_prefix}info"
            )
        )

    async def on_message(self, message):
        owner = self.owner_ids[0] or self.owner_id or None
        owner = self.get_user(owner)
        guild = None
        if message.channel.type is not discord.ChannelType.private:
            guild = await utility.db_for_guild(message.guild.id, True)

        if guild:
            if guild.blacklisted:
                return
        user = None
        user = await utility.db_for_user(message.author.id, True)
        if message.author.bot:
            return
        if not user.canUseBot:
            return
        swregex = r"(^\W|d::|^```)"
        if len(message.content) > 8 and not re.match(swregex, message.content):
            if message.channel.type is not discord.ChannelType.private:
                if message.guild.id in self.allowedLearningGuilds:
                    corpus.write(message.content.lower() + "\n")

        if (message.channel.type == discord.ChannelType.private) and owner:
            if message.author is not owner:
                await owner.send(f"`DM from {message.author} ({message.author.id}):`\n{message.content}")

        if (self.user in message.mentions) or (random.random() < 0.008):
            if random.choice([True, False]):
                await message.channel.send(utility.call_markov(900))
            else:
                await message.channel.send(utility.call_cmarkov(900))

        await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        delay = 10
        excname = type(exception).__name__
        errembed = discord.Embed(
            title=f"{excname} error",
            description=str(exception),
            color=0xAA0000
        )

        if isinstance(exception, commands.CommandNotFound):
            commandnames = []
            failed = str(exception).split(" ")
            failed = failed[1]
            parsedfailed = failed.replace("\"", "")
            
            for command in ctx.bot.commands:
                commandnames.append(command.name)
                for alias in command.aliases:
                    if alias == "":
                        return
                    commandnames.append(alias)
            
            matches = difflib.get_close_matches(parsedfailed, commandnames, 6, 0.5)
            if len(matches) == 0:
                return
            dymembed = discord.Embed(
                title=f"Couldn't find command {failed}",
                color=0xff0000,
                description="Did you mean..."
            )
            for match in matches:
                dymembed.add_field(name=f"{ctx.bot.command_prefix}{match}?", value="\u202d")

            await ctx.send(embed=dymembed)
            return

        if excname != "CommandOnCooldown":  # dont need cooldowns logged
            print(f"{excname}: {exception}")
        errmsg = await ctx.send(embed=errembed)
        await errmsg.delete(delay=delay)

    async def on_member_join(self, member):
        guild = member.guild
        guilddb = await LBGuild.filter(id=guild.id).first()
        joinmsg = getattr(guilddb, "joinMesg")
        chid = getattr(guilddb, "joinMesgChannel")
        joinmsgchannel = self.get_channel(chid) or guild.system_channel
        if (joinmsg is not None) and (joinmsgchannel is not None):
            jmsg = joinmsg.replace("%member%", member.mention)
            await joinmsgchannel.send(f"{jmsg}")

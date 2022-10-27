import datetime
import difflib
import json
import random
import re

import discord
from discord.ext import commands, tasks

import utility.funcs as utility
from classes.dbmodels import LBGuild

corpus = open("corpus.txt", "at", encoding="utf-8")
started_at = datetime.datetime.now()
cooldown_texts = ["Hey there.", "Hold on a second!", "pls wait...", "Cooldown..", "Hey, chill.",
                  "Just a minute...", "Give it a second.", "Whoop", "..."]

status_texts = ["with pip", "with python", "with you", "with bot.py", "with git", "mind games", "ooer game",
                "minecraft", "with bash", "with linux", "games", "with discord.py",
                "with frogs", "with cats", "with dogs", "you", "vs code", "around", "with knives", "with destruction",
                "with bombs", "with myself", "with your mom", "with your dad", "with crewmates", "."]


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
            user_count = random.choice(status_texts)
        except Exception:
            user_count = "with you"

        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"{user_count} | {self.command_prefix}help"
            )
        )

    async def on_message(self, message: discord.Message):
        owner = self.owner_ids[0] or self.owner_id or None
        owner = self.get_user(owner)
        guild = None
        if message.channel.type is not discord.ChannelType.private:
            guild = await utility.db_for_guild(message.guild.id, True)
            mkv = await utility.db_for_mkv(message.guild.id, True)
            chatchannel = await utility.db_for_mkv_channel(message.channel.id, True)

        if guild:
            if guild.blacklisted:
                return
        user = None
        user = await utility.db_for_user(message.author.id, True)

        if message.author.bot or not user.canUseBot:
            return

        swregex = r"(^\W|d::|^```|ooer )"
        pingregex = r"^<@"
        if len(message.content) > 8:
            if re.match(pingregex, message.content) or not re.match(swregex, message.content):
                if message.channel.type is not discord.ChannelType.private:
                    if message.guild.id in self.allowedLearningGuilds:
                        pass
                        corpus.write(message.content + "\n")

        if (message.channel.type == discord.ChannelType.private) and owner:
            if message.author is not owner:
                await owner.send(f"`DM from {message.author} ({message.author.id}):`\n{message.content}")

        canmkv = mkv and mkv.enabled
        is_chat_channel = chatchannel and chatchannel.enabled

        if (self.user in message.mentions) or (random.random() < 0.008 and canmkv) or is_chat_channel:
            try:
                msg = utility.call_markov(900)
            except AttributeError:
                return
            firstmsg = msg

            if random.randint(0, 20) == 10:
                msg = utility.call_markov(900, message.author.mention)
            if "appear enough in the corpus" in msg:  # I am a victim of my own bad code
                msg = firstmsg

            await message.channel.send(msg)

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

        if isinstance(exception, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)

        if isinstance(exception, Exception):  # we will be throwing generic exceptions in commands, fuck you
            ctx.command.reset_cooldown(ctx)

        if isinstance(exception, commands.CommandOnCooldown):
            errembed.title = random.choice(cooldown_texts)
        else:
            print(f"{excname}: {exception}")

        errmsg = await ctx.send(embed=errembed)
        await errmsg.delete(delay=delay)

    async def on_member_join(self, member):
        guild = member.guild
        guilddb = await LBGuild.filter(id=guild.id).first()
        joinmsg = getattr(guilddb, "joinMesg") or None
        chid = getattr(guilddb, "joinMesgChannel") or None
        joinmsgchannel = self.get_channel(chid) or guild.system_channel
        if (joinmsg is not None) and (joinmsgchannel is not None):
            jmsg = joinmsg.replace("%member%", member.mention)
            await joinmsgchannel.send(f"{jmsg}")

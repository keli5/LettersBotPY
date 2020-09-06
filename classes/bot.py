import discord
from classes.dbmodels import LBGuild
import utility.funcs as utility
import datetime
from discord.ext import commands, tasks
import re
import random
typedescs = {
    "\"int\"": "number without a decimal point",
    "\"str\"": "string of text",
    "\"float\"": "number, optionally with up to 2 decimal places"
}
type_examples = {
    "\"int\"": "11",
    "\"str\"": "Hello, World!",
    "\"float\"": "48.92"
}
corpus = open("corpus.txt", "a")
started_at = datetime.datetime.now()


class LettersBot(commands.AutoShardedBot):  # when you going
    """ Welcome to the rewrite of LettersBot! """
    async def on_ready(self):
        self.allowedLearningGuilds = [554079640499519499, 671897656003395595, 726699349362343967,
                                      699476987990769735, 672963999964594176, 505508859117305877]
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
            return

        if isinstance(exception, commands.BadArgument):
            string = str(exception).split(" ")
            if len(string) == 7:
                delay = 20
                type_to_be = string[2]
                argument = string[6]
                argument = argument[0:len(argument)-1]
                try:
                    errembed.add_field(
                        name="How to fix it?",
                        value=f"Argument {argument} failed to convert; it needs to be a {typedescs[type_to_be]}."
                    )
                except KeyError:
                    pass
                try:
                    errembed.add_field(
                        name=f"Example of {type_to_be}",
                        value=type_examples[type_to_be]
                    )
                except KeyError:
                    pass

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

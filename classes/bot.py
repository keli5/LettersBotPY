import discord
import os
from tortoise.models import Model
from classes.dbmodels import LBGuild, LBUser
from utility.funcs import setup
import json
from discord.ext import commands

class LettersBot(commands.AutoShardedBot): # when you going
    async def on_ready(self):
        await setup()
        await self.change_presence(activity=discord.Game(name='with your mind'))
        print("Ready!")
    
    async def on_message(self, message):
        if message.author.bot: return
        guild = ""
        user = ""
        try:
            user = await LBUser.get(id=message.author.id)
        except:
            user = await LBUser.create(
                id=message.author.id,
                balance=0,
                canUseBot=True,
                inventory=[],
                warnings=[],
                banUntil=None
            )
            print(f"Created entry for {message.author}")
        try:
            guild = await LBGuild.get(id=message.guild.id)
        except:
            guild = await LBGuild.create(
                id=message.guild.id,
                muteRole=0,
                joinMesg=None
            )
            print(f"Created entry for {message.guild}")
        if user.canUseBot == True:
            await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandNotFound):
            return

        errembed = discord.Embed(
            title="An error occurred.",
            description=str(exception),
            color=0xAA0000
        )
        await ctx.send(embed=errembed)

    async def on_member_join(self, member):
        guild = member.guild
        guilddb = await LBGuild.filter(id=guild.id).first()
        joinmsg = getattr(guilddb, "joinMesg")
        joinmsgchannel = self.get_channel(getattr(guilddb, "joinMesgChannel")) or guild.system_channel
        if (joinmsg is not None) and (joinmsgchannel is not None):
            await joinmsgchannel.send(f"{member.mention}\n{joinmsg}")






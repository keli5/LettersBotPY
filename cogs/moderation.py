from discord.ext import commands, tasks
import discord
from classes.dbmodels import LBUser, LBGuild

def __init__(self, bot):
    self.bot = bot
    self.check_for_updates.start()

class Moderation(commands.Cog):

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user:discord.Member, *, reason:str = "No reason provided"):
        ''' Kick a user from the guild. '''
        await ctx.guild.kick(user, reason=reason)
        kickembed = discord.Embed(
            title=f"Kicked {str(user)} from {str(ctx.guild)}",
            color=0xAA0000
        )
        kickembed.add_field(name="Reason", value=reason)
        kickembed.add_field(name="ID", value=user.id)
        await ctx.send(embed=kickembed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user:discord.Member, *, reason:str="No reason provided"):
        ''' Ban a user from the guild. '''
        await ctx.guild.ban(user, reason=reason)
        banembed = discord.Embed(
            title=f"Banned {str(user)} from {str(ctx.guild)}",
            color=0xAA0000
        )
        banembed.add_field(name="Reason", value=reason)
        banembed.add_field(name="ID", value=user.id)
        await ctx.send(embed=banembed)

    @commands.command(aliases=["pardon"])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, userid:discord.User, *, reason:str="No reason provided."):
        ''' Unban a user from the guild. '''
        await ctx.guild.unban(userid, reason=reason)
        unbanembed = discord.Embed(
            title=f"Unbanned {str(userid)} from {str(ctx.guild)}",
            color=0x00AA00 # green because the victim has been freed
        )
        unbanembed.add_field(name="Reason", value=reason)
        unbanembed.add_field(name="ID", value=userid.id)
        await ctx.send(embed=unbanembed)



    @commands.group(aliases=["joinmessage"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def joinmsg(self, ctx):
        ''' Commands to manipulate the guild's custom join message. '''
        joinmsg = await LBGuild.filter(id=ctx.guild.id).first()
        joinmsg = getattr(joinmsg, "joinMesg")
        await ctx.send('This guild' + (" has no join message." if joinmsg == None else f"\'s join message is: \n{joinmsg}"))

    @joinmsg.command()
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx, *, joinmessage:str):
        ''' Set the guild's custom join message. '''
        if (len(joinmessage) > 1350):
            return await ctx.send('Guild join messages may only be a max of 1,350 characters long.')
        await LBGuild.filter(id=ctx.guild.id).update(joinMesg=joinmessage)
        await ctx.send('Successfully updated guild join message.')

    @joinmsg.command(aliases=["delete", "reset"])
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx):
        ''' Remove the guild's custom join message. '''
        await LBGuild.filter(id=ctx.guild.id).update(joinMesg=None)
        await ctx.send('Successfully removed guild join message.')


def cog_unload(self):
    self.check_for_updates.cancel()

def setup(bot):
    bot.add_cog(Moderation(bot))
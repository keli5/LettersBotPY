from discord.ext import commands, tasks
import discord

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
        user = userid #todo: replace user instances with userid instead
        """ Unban a user from the guild. """
        await ctx.guild.unban(user, reason=reason)
        unbanembed = discord.Embed(
            title=f"Unbanned {str(user)} from {str(ctx.guild)}",
            color=0x00AA00 # green because the victim has been freed
        )
        unbanembed.add_field(name="Reason", value=reason)
        unbanembed.add_field(name="ID", value=user.id)
        await ctx.send(embed=unbanembed)


def cog_unload(self):
    self.check_for_updates.cancel()
def setup(bot):
    bot.add_cog(Moderation(bot))
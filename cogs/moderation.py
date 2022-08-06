from diskord.ext import commands
import diskord
from classes.dbmodels import LBGuild, GuildMarkovSettings, GuildChatChannel
alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 10):
        """ Delete <amount> messages in this channel. """
        if amount > 100:
            await ctx.send("Max amount is 100.")
        if amount < 2:
            await ctx.send("Minimum amount is 2.")
        await ctx.channel.purge(limit=amount)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user: diskord.Member, *, reason: str = "No reason provided."):
        """Kick a user from the guild."""
        await ctx.guild.kick(user, reason=reason)
        kickembed = diskord.Embed(
            title=f"Kicked {str(user)} from {str(ctx.guild)}",
            color=diskord.Color.red()
        )

        kickembed.add_field(name="Reason", value=reason)
        kickembed.add_field(name="ID", value=user.id)
        await ctx.send(embed=kickembed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: diskord.Member, *, reason: str = "No reason provided"):
        """Ban a user from the guild."""
        await ctx.guild.ban(user, reason=reason)
        banembed = diskord.Embed(
            title=f"Banned {str(user)} from {str(ctx.guild)}",
            color=diskord.Color.red()
        )

        banembed.add_field(name="Reason", value=reason)
        banembed.add_field(name="ID", value=user.id)
        await ctx.send(embed=banembed)

    @commands.command(aliases=["pardon"])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, userid: diskord.User, *, reason: str = "No reason provided."):
        """Unban a user from the guild."""
        await ctx.guild.unban(userid, reason=reason)
        unbanembed = diskord.Embed(
            title=f"Unbanned {str(userid)} from {str(ctx.guild)}",
            color=diskord.Color.green()  # green because the victim has been freed
        )
        unbanembed.add_field(name="Reason", value=reason)
        unbanembed.add_field(name="ID", value=userid.id)
        await ctx.send(embed=unbanembed)

    @commands.command(aliases=["togglespeak", "togglemkv"])
    @commands.has_permissions(manage_guild=True)
    async def togglerandommkv(self, ctx):
        """ Allow or disallow the bot from randomly speaking. """
        markov = await GuildMarkovSettings[ctx.guild.id]
        can = getattr(markov, "enabled")
        await GuildMarkovSettings.filter(id=ctx.guild.id).update(enabled=(not can))
        await ctx.send(f"Toggled random markov messages. This bot **{'can' if not can else 'can not'}** randomly speak in this server.")  # noqa: E501

    @commands.command(aliases=["chatchannel"])
    @commands.has_permissions(manage_guild=True)
    async def togglechatchannel(self, ctx):
        """ Allow or disallow the bot from responding to every message in this channel. """
        markov = await GuildChatChannel[ctx.channel.id]
        can = getattr(markov, "enabled")
        await GuildChatChannel.filter(id=ctx.channel.id).update(enabled=(not can))
        await ctx.send(f"Toggled chat channel. This bot **{'can' if not can else 'can not'}** respond to each message in this channel.")  # noqa: E501

    @commands.group(aliases=["joinmessage"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def joinmsg(self, ctx):
        """Commands to manipulate the guild's custom join message."""
        joinmsg = await LBGuild.filter(id=ctx.guild.id).first()
        joinmsg = getattr(joinmsg, "joinMesg")
        await ctx.send("This guild" + (f"'s join message is: \n{joinmsg}" if joinmsg else " has no join message."))

    @joinmsg.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def set_join_message(self, ctx, *, joinmessage: str):
        """Set the guild's custom join message. Add %member% to mention whoever joined."""
        if len(joinmessage) > 1350:
            return await ctx.send("Guild join messages may only be a max of 1,350 characters long.")

        await LBGuild.filter(id=ctx.guild.id).update(joinMesg=joinmessage)
        await ctx.send("Successfully updated guild join message.")

    @joinmsg.command(name="remove", aliases=["delete", "reset"])
    @commands.has_permissions(manage_guild=True)
    async def remove_cjm(self, ctx):
        """Remove the guild's custom join message."""
        await LBGuild.filter(id=ctx.guild.id).update(joinMesg=None)
        await ctx.send("Successfully removed guild join message.")

    @joinmsg.command(aliases=["setchannel"])
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx, channel: diskord.TextChannel):
        """Set the channel for the custom join message."""
        myself = ctx.guild.get_member(ctx.bot.user.id)
        if not channel.permissions_for(myself).send_messages:
            return await ctx.send("This channel won't work - the bot can't speak in it.")

        await LBGuild.filter(id=ctx.guild.id).update(joinMesgChannel=channel.id)
        await ctx.send(f"Successfully set {channel.name} as the join message channel.")

    @joinmsg.command()
    @commands.has_permissions(manage_guild=True)
    async def resetchannel(self, ctx):
        """Reset to the default channel."""
        await LBGuild.filter(id=ctx.guild.id).update(joinMesgChannel=None)
        await ctx.send(f"Successfully reset the join message channel to {ctx.guild.system_channel}.".capitalize())


def setup(bot):
    bot.add_cog(Moderation(bot))

from discord.ext import commands
import discord
import typing
import platform as p
import pkg_resources


def version(package_name):
    """ A tiny function to shorten getting package versions. """
    return pkg_resources.get_distribution(package_name).version


class Utility(commands.Cog):
    ''' Quick utility commands that provide mostly information '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        ''' Show the bot's ping. '''
        await ctx.send(f"Ponged in **{round(self.bot.latency * 1000, 2)}ms.**")

    @commands.group(invoke_without_command=True, aliases=["os"])
    async def osinfo(self, ctx):
        """ Show some info about what the bot's running on, package versions, and more. """
        packages_for_info = ["discord.py", "tortoise-orm", "markovify", "pillow"]
        osembed = discord.Embed(
            title=ctx.bot.user.name,
            color=discord.Color.purple()
        )
        py_ver = p.python_version()
        osembed.add_field(name="Python version", value=py_ver, inline=False)
        for package in packages_for_info:
            osembed.add_field(name=f"**{package}** version", value=version(package))
        os_ver = f"{p.system()} {p.release()}"
        osembed.add_field(name="OS type", value=os_ver or "Unknown")
        osembed.add_field(name="Architecture", value=p.processor() or "Unknown")
        await ctx.send(embed=osembed)

    @osinfo.command(aliases=["pkg"])
    async def packages(self, ctx):
        pkgembed = discord.Embed(
            title="Required packages",
            color=discord.Color.purple()
        )
        with open("requirements.txt") as f:
            packages = f.read().split(" ")[0::2][0::2]
            for pkg in packages:
                pkgembed.add_field(name=pkg, value=version(pkg))

        await ctx.send(embed=pkgembed)

    @commands.command(aliases=["a"])
    async def avatar(self, ctx, user: discord.User = None):
        ''' Get somebody's avatar, or your own. '''
        victim = user or ctx.author
        avatarembed = discord.Embed(
            title=f"Avatar of {str(victim)}",
            color=victim.color
        )
        avatarembed.set_image(url=victim.avatar_url)
        await ctx.send(embed=avatarembed)

    @commands.command()
    async def userinfo(self, ctx, user: discord.Member = None):
        ''' Get some info about a user, or yourself. '''
        user = user or ctx.author
        uiembed = discord.Embed(
            title=f"User info about {str(user)}",
            color=user.color,
            description="Dates are in mm/dd/yy HH:MM:SS format, UTC"
        )
        uiembed.add_field(
            name="Joined guild at",
            value=user.joined_at.strftime("%m/%d/%Y %H:%M") + " UTC"
        )
        uiembed.set_thumbnail(url=str(user.avatar_url))
        uiembed.add_field(name="Nickname", value=user.nick or "No nickname")
        rolestring = ""
        nroles = []
        for role in user.roles:
            nroles.append(role.name)
        if len(nroles) > 4:
            rolestring = f"{', '.join(nroles[1:4])} and {len(nroles) - 4} more"
        else:
            rolestring = ", ".join(nroles[1:4])
        uiembed.add_field(name="Roles", value=rolestring, inline=len(nroles) < 4)
        uiembed.add_field(name="ID", value=user.id)
        uiembed.add_field(name="Boosting?", value="Yes" if user.premium_since else "No")
        uiembed.add_field(name="On mobile", value="Yes" if user.is_on_mobile() else "No")
        await ctx.send(embed=uiembed)

    @commands.command()
    async def bigmoji(self, ctx, emoji: typing.Union[discord.PartialEmoji, str]):
        """ Get the full-size image of an emoji. """
        if isinstance(emoji, discord.PartialEmoji):
            url = str(emoji.url)
        else:
            cpoint = str(hex(ord(emoji[0])))
            cpoint = cpoint[2:]
            if cpoint[0:2] != "1f":
                return await ctx.send("Invalid emoji.")
            url = f"https://twemoji.maxcdn.com/v/12.1.6/72x72/{cpoint}.png"
        bmembed = discord.Embed(
            title="Full-size emoji",
            url=url,
            color=discord.Color.green()
        )
        bmembed.set_image(url=url)
        await ctx.send(embed=bmembed)

    @commands.command()
    async def info(self, ctx):
        iembed = discord.Embed(
            title="LettersBot",
            description="LettersBot started out as a little JavaScript bot hosted on my Chromebook, " +
                        "now rewritten in Python with its own room among a few other great bots! " +
                        "Feel free to invite the bot to your server, play around with it, " +
                        "and tell me about bugs on the GitHub repo!",
            color=discord.Color.gold()
        )
        iembed.set_thumbnail(url=ctx.bot.user.avatar_url)
        iembed.add_field(name="Home/support server", value="https://discord.gg/rXVnuTB")
        iembed.add_field(
            name="Invite the bot",
            value="https://cutt.ly/lettersbot",
            inline=False
        )
        iembed.add_field(name="Patreon", value='https://patreon.com/lettersbot', inline=False)
        iembed.add_field(name="GitHub", value="https://github.com/keli5/LettersBotPY")
        letters = ctx.bot.get_user(556614860931072012)
        iembed.set_footer(
            text=f"Made by Letters ({letters})",
            icon_url=letters.avatar_url
        )
        await ctx.send(embed=iembed)


def setup(bot):
    bot.add_cog(Utility(bot))

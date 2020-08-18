from discord.ext import commands
import discord
import typing
import utility.funcs as f
import platform as p
import pkg_resources
import aiohttp
import classes.bot as bot
import humanize
import json


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
        osembed.add_field(name="Python version", value=py_ver)
        osembed.add_field(name="System uptime", value=humanize.precisedelta(f.get_uptime(), minimum_unit="seconds"))
        osembed.add_field(name="Bot uptime", value=humanize.precisedelta(bot.started_at, minimum_unit="seconds",
                          format="%0.0f", suppress=["months", "years"]))

        for package in packages_for_info:
            osembed.add_field(name=f"**{package}** version", value=version(package))
        os_ver = f"{p.system()} {p.release()}"
        osembed.add_field(name="OS type", value=os_ver or "Unknown")
        osembed.add_field(name="Architecture", value=p.machine() or p.processor() or "Unknown")
        await ctx.send(embed=osembed)
# todo: osinfo packages needs to be fixed

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

    @commands.group(aliases=["pypi"], invoke_without_command=True)
    async def pip(self, ctx, package: str = "discord.py"):
        """Get information about a package from PyPI."""
        packageinfo = None
        if len(package.split()) > 1:
            return await ctx.send("Package names cannot contain spaces.")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"https://pypi.org/pypi/{package}/json") as r:
                    r = await r.content.read()
                    packageinfo = json.loads(r)
                    packageinfo = packageinfo["info"]
            except Exception:
                return await ctx.send(f"Couldn't get package {package} from PyPI.")
        gpiembed = discord.Embed(
            title=package,
            color=0x4B8BBE,
            description=packageinfo["summary"],
            url=packageinfo["package_url"]
        )
        gpiembed.add_field(name="Author", value=packageinfo["author"])
        gpiembed.add_field(name="Python version", value=packageinfo["requires_python"] or "Unknown")
        gpiembed.add_field(name="Package version", value=packageinfo["version"])
        if packageinfo["docs_url"]:
            gpiembed.add_field(name="Docs", value=packageinfo["docs_url"], inline=False)

        otherdocs = None  # why must it be this way
        if packageinfo["project_urls"] is not None:
            if "Documentation" in packageinfo["project_urls"]:
                otherdocs = packageinfo["project_urls"]["Documentation"]
            if "Docs" in packageinfo["project_urls"]:
                otherdocs = packageinfo["project_urls"]["Docs"]

        if otherdocs:
            gpiembed.add_field(name="Docs", value=otherdocs, inline=False)
        if packageinfo["license"]:
            gpiembed.add_field(name="License", value=packageinfo["license"])

        await ctx.send(embed=gpiembed)

    @pip.command(aliases=["downloads", "files", "releases"])
    async def release(self, ctx, package: str = "discord.py", version=None):
        # return await ctx.send("This is not done")

        packageinfo = None
        packageval = None
        if len(package.split()) > 1:
            return await ctx.send("Package names cannot contain spaces.")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://pypi.org/pypi/{package}/json") as r:
                r = await r.content.read()
                packageval = json.loads(r)
                packageinfo = packageval["info"]
        ver = version or packageinfo["version"]
        releases = packageval["releases"]
        if ver not in releases:
            return await ctx.send(f"Version {ver} does not exist.")
        release = packageval["releases"][ver]
        try:
            release = release[1]
        except IndexError:
            release = release[0]
        rURL = release["url"]
        rlembed = discord.Embed(
            title=f"{package} v{ver}",
            color=0x4B8BBE,
            description=f"{package} has {len(releases)} releases"
        )
        rlembed.add_field(name="Download", value=f"[Get the latest for {ver}]({rURL})")
        rsize = release["size"]
        rlembed.add_field(name="Size", value=humanize.naturalsize(rsize))
        await ctx.send(embed=rlembed)

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

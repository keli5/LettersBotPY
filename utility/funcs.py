import datetime
import io
import aiohttp
import random
import re
import typing
import markovify
from PIL import Image
from tortoise import Tortoise
from classes.dbmodels import GuildMarkovSettings, LBUser, LBGuild, GuildChatChannel
from classes.cmarkov import CharacterText
markov = None
cmarkov = None


eightball = [
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful",
    "Reply hazy, try again",
    "Ask again later",
    "Better not tell you now",
    "Cannot predict now",
    "Concentrate and ask again",
    "As I see it, yes",
    "It is certain",
    "It is decidedly so",
    "Most likely",
    "Outlook good",
    "Signs point to yes",
    "Without a doubt",
    "Yes",
    "Yes - definitely",
    "You may rely on it",
]


async def setup():
    await Tortoise.init(
        db_url='sqlite://lettersbot_data.sqlite3',
        modules={'models': ["classes.dbmodels"]}
    )

conv_dict = {
    'd': 'days',
    'h': 'hours',
    'm': 'minutes',
    's': 'seconds',
}
pat = r"[0-9]+[s|m|h|d]{1}"


def super_secret_8ball():
    return random.choice(eightball)


def timestr_to_dict(tstr):
    'e.g. convert 1d2h3m4s to {"d": 1, "h": 2, "m": 3, "s": 4}'
    return {conv_dict[p[-1]]: int(p[:-1]) for p in re.findall(pat, tstr)}


def timestr_to_seconds(tstr):
    return datetime.timedelta(**timestr_to_dict(tstr)).total_seconds()
# Use timestr_to_seconds() to get an amount of seconds out of it
# A timestr looks something like "5h30m" or "7d"


async def db_for_user(id: int, returns: bool = False) -> dict:
    """Tries to get the DB entry for user with id `id`, if it doesn't work,
    generates a DB entry for them.
    Also returns the user if `returns` is true."""
    try:
        user = await LBUser[id]
    except KeyError:
        user = await LBUser.create(
            id=id,
            balance=0,
            canUseBot=True,
            inventory={}
        )

    if returns is True:
        return user


async def db_for_guild(id: int, returns: bool = False) -> dict:
    """ Tries to get the DB entry for guild with id `id`, if it doesn't work,
    generates a DB entry for it.
    Also returns the guild if `returns` is true. """
    try:
        guild = await LBGuild[id]
    except KeyError:
        guild = await LBGuild.create(
            id=id,
            muteRole=0,
            joinMesg=None,
            disabledCommands=[],
            blacklisted=False
        )

    if returns is True:
        return guild


async def db_for_mkv(id: int, returns: bool = False) -> dict:
    """ Same as db_for_user/guild, with markov settings. """
    try:
        mkv = await GuildMarkovSettings[id]
    except KeyError:
        mkv = await GuildMarkovSettings.create(
            id=id,
            enabled=True
        )

    if returns is True:
        return mkv


async def db_for_mkv_channel(id: int, returns: bool = False) -> dict:
    """ Same as the other shit but mkv channels """
    try:
        mkv = await GuildChatChannel[id]
    except KeyError:
        mkv = await GuildChatChannel.create(
            id=id,
            enabled=False
        )

    if returns is True:
        return mkv


async def image_from_url(source) -> Image:
    """ Takes a url of an image as `source`. Returns a Pillow image. """
    async with aiohttp.ClientSession() as session:
        if not source:
            raise Exception("No image provided.")
        async with session.get(source) as resp:
            img = await resp.content.read()
        try:
            img = Image.open(io.BytesIO(img))
        except OSError as exc:
            raise exc

    return img


def shuffle_tuple(tuple):
    """ Takes tuple `tuple` and returns the new, shuffled version of it. """
    tl = []
    for item in tuple:
        tl.append(item)
    shuffled = random.sample(tl, len(tl))
    shuffled = (*shuffled, )  # "tuple" object is apparently not callable
    return shuffled


def image_to_byte_array(image: Image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    return list(img_byte_arr)


def tally_users(bot) -> int:
    count = 0
    users_seen = []
    for guild in bot.guilds:
        for member in guild.members:
            if member.id not in users_seen:
                users_seen.append(member.id)
                count += 1
    return count


def reload_markov():
    with open("corpus.txt", encoding="utf-8") as f:
        corpus = f.read()
    try:
        global markov
        global cmarkov
        markov = markovify.NewlineText(corpus)
        cmarkov = CharacterText(corpus, state_size=3)
    except Exception as e:
        print("Markov will not work - an error occurred:")
        print(e)


def call_markov(maxlength, startword: str = None) -> str:
    try:
        if startword:
            sentence = markov.make_sentence_with_start(
                startword,
                max_chars=maxlength,
                strict=True,
                tries=200
                )
        else:
            sentence = markov.make_short_sentence(maxlength)
    except KeyError:
        sentence = f"`{startword}` does not appear enough in the corpus."
    sentence = sentence or "Failed to generate a sentence."
    sentence = sentence.replace("@everyone", "everyone")
    sentence = sentence.replace("@here", "here")
    return sentence


def call_cmarkov(maxlength, startword: str = None) -> str:
    try:
        if startword:
            sentence = cmarkov.make_sentence_with_start(
                startword,
                max_chars=maxlength,
                strict=True,
                tries=200
                )
        else:
            sentence = cmarkov.make_short_sentence(maxlength)
    except KeyError:
        sentence = f"`{startword}` does not appear enough in the corpus."
    sentence = sentence or "Failed to generate a sentence."
    sentence = sentence.replace("@everyone", "everyone")
    sentence = sentence.replace("@here", "here")
    return sentence


def paginate_list(list_items: typing.Union[list, tuple],
                  per_page: int = 10, page: int = 1) -> list:  # ?????
    page = page - 1
    start = (page * per_page)
    stop = start + per_page
    return list_items[start:stop]


def get_uptime():  # lifted directly from S/O: https://stackoverflow.com/a/55109870/12082547
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    return uptime_seconds


def enumerate_list(list_items: typing.Union[list, tuple], max_shown: int) -> str:
    newlist = []
    string = ""
    for item in list_items:  # in case we have a tuple
        newlist.append(item)
    if len(newlist) > max_shown:
        string = f"{', '.join(newlist[0:max_shown])} and {len(newlist) - max_shown} more"
    else:
        string = ", ".join(newlist[0:max_shown])
    return string


def command_from_name(name: str, ctx):  # I hate this with every fiber
    command = None                      # of my being
    for cmd in ctx.bot.commands:
        if cmd.name == name:
            command = cmd
            break
        if name in cmd.aliases:
            command = cmd
            break
    return command

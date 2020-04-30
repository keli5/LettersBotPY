import datetime
from PIL import Image
import io
import requests
import re
from tortoise import Tortoise
import tortoise.exceptions
from classes.dbmodels import LBUser


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


def timestr_to_dict(tstr):
    'e.g. convert 1d2h3m4s to {"d": 1, "h": 2, "m": 3, "s": 4}'
    return {conv_dict[p[-1]]: int(p[:-1]) for p in re.findall(pat, tstr)}


def timestr_to_seconds(tstr):
    return datetime.timedelta(**timestr_to_dict(tstr)).total_seconds()
# Use timestr_to_seconds() to get an amount of seconds out of it
# A timestr looks something like "5h30m" or "7d"


async def db_for_user(id: int, returns: bool = False) -> dict:
    """Tries to get the DB entry for user with id `id`, if it doesn't work, generates a DB entry for them.
    Also returns the user if `returns` is true."""
    try:
        user = await LBUser.get(id=id)
    except tortoise.exceptions.DoesNotExist:
        user = await LBUser.create(
            id=id,
            balance=0,
            canUseBot=True,
            inventory={},
            warnings={},
            banUntil=None
        )

    if returns is True:
        return user

async def image_from_url(source, ctx) -> Image:
        if not source:
            return await ctx.send("No image was provided.")
        img = io.BytesIO(requests.get(source).content)
        try:
            img = Image.open(img)
        except OSError:
            return await ctx.send("There was an error opening the image.")

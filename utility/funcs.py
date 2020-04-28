from tortoise import Tortoise
import json
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
pat = r'[0-9]+[s|m|h|d]{1}'
def timestr_to_dict(tstr):
    'e.g. convert 1d2h3m4s to {"d": 1, "h": 2, "m": 3, "s": 4}'
    return {conv_dict[p[-1]]: int(p[:-1]) for p in re.findall(pat, test_str)}
def timestr_to_seconds(tstr):
    return datetime.timedelta(**timestr_to_dict(tstr)).total_seconds()
# Use timestr_to_seconds() to get an amount of seconds out of it
# A timestr looks something like "5h30m" or "7d"

from classes.bot import LettersBot
from discord.ext.commands import Paginator
from help_command import PaginatedHelpCommand
import os
import json

extlist = ["jishaku", "utility", "moderation", "images", "economy", "owner", "fun", "voice"]
botprefix = ""

try:
    botprefix = os.environ['LB_PREFIX']
except KeyError:
    botprefix = "d::"

with open("classes/botowners.txt", "r") as botowners:
    paginator = Paginator(max_size=1336)  # see help_command.py

    bot = LettersBot(  # create the bot
        command_prefix=botprefix,
        case_insensitive=True,
        owner_ids=json.loads(botowners.read()),
        help_command=PaginatedHelpCommand(paginator=paginator)  # see help_command.py
    )

if not os.path.exists("lettersbot_data.sqlite3"):
    print('Running initdb.py')
    exec(open("utility/initdb.py").read())

for extension in extlist:
    prefix = "cogs."
    if extension == "jishaku":
        prefix = ""
    try:
        bot.load_extension(prefix + extension)
        print('Successfully loaded extension ' + extension)
    except Exception as e:
        exc = "{}: {}".format(type(e).__name__, e)
        print(f"Failed to load extension {extension}\nError: {exc}")

bot.run(os.environ['BOT_TOKEN'])

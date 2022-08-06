from classes.bot import LettersBot
from diskord.ext.commands import Paginator
import utility.initdb as i
import diskord
from tortoise import run_async
# from help_command import PaginatedHelpCommand
# import os
import json

extlist = ["jishaku", "utility", "moderation", "images", "economy", "owner", "fun"]
botprefix = ""
token = ""
intents = diskord.Intents.all()  # reactions.

try:
    with open("config.json") as opts:
        opts = json.loads(opts.read())
        botprefix = opts["prefix"] or "d::"
        token = opts["token"]
except Exception as e:
    print("Something went wrong. Make sure your config.json is valid and all keys are filled in.")
    print(e)
    exit()


with open("classes/botowners.txt", "r") as botowners:
    paginator = Paginator(max_size=1336)  # see help_command.py

    bot = LettersBot(  # create the bot
        command_prefix=botprefix,
        case_insensitive=True,
        owner_ids=json.loads(botowners.read()),
        # help_command=PaginatedHelpCommand(paginator=paginator),  # see help_command.py
        intents=intents
    )

# if not os.path.exists("lettersbot_data.sqlite3"):
# fuck
print('Running initdb.py')
run_async(i.init())

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

bot.run(token)

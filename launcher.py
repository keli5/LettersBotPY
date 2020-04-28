from classes.bot import LettersBot
import os
import json

extlist = ["jishaku", "utils"] # Add extensions to this list by filename when you add one. Shocking I know
# Remove jishaku from the list for deployment

botowners = open("classes/botowners.txt", "r")
bot = LettersBot( # create the bot
    command_prefix="d::",
    case_insensitive=True,
    owner_ids=json.loads(botowners.read())
)
botowners.close()

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
      exc = '{}: {}'.format(type(e).__name__, e)
      print('Failed to load extension {}\nError: {}'.format(extension, exc))

bot.run(os.environ['BOT_TOKEN'])
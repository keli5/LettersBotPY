from classes.bot import LettersBot

botowners = open("models/botowners.txt", "r")
bot = LettersBot( # create the bot
    command_prefix="d::",
    case_insensitive=True,
    owner_ids=json.loads(botowners.read())
)
botowners.close()



bot.run(os.environ['BOT_TOKEN'])
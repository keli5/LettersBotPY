import discord
import os
from discord.ext import commands
extlist = ["jishaku", "utils"] # Add extensions to this list by filename when you add one. Shocking I know
# Remove jishaku from the list for deployment

class LettersBot(commands.AutoShardedBot): # when you going
    async def on_message(self, message):

        await self.process_commands(message)


bot = LettersBot( # create the bot
    command_prefix="d::",
    case_insensitive=True
)

if __name__ == "__main__":    # Importing extensions
  for extension in extlist:
    try:
      bot.load_extension(extension)
      print('Successfully loaded extension ' + extension)
    except Exception as e:
      exc = '{}: {}'.format(type(e).__name__, e)
      print('Failed to load extension {}\nError: {}'.format(extension, exc))


bot.run(os.environ['BOT_TOKEN'])
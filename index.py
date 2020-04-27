import discord
import os
from tortoise.models import Model
from models import LBUser, LBGuild
from utilfuncs import setup
from discord.ext import commands
extlist = ["jishaku", "utils"] # Add extensions to this list by filename when you add one. Shocking I know
# Remove jishaku from the list for deployment

class LettersBot(commands.AutoShardedBot): # when you going
    async def on_ready(self):
        await setup()
        print("Ready!")
    
    async def on_message(self, message):
        if message.author.bot: return
        user = await LBUser.get_or_create(defaults={
            "id": message.author.id,
            "balance": 0,
            "canUseBot": True,
            "inventory": []
        })
        guild = await LBGuild.get_or_create(defaults={
            "id": message.guild.id,
            "muteRole": 0,
        })
        if user[1] == True:
            print(f'Created entry for {message.author}')
        if guild[1] == True:
            print(f'Created entry for {message.guild}')
        await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandNotFound):
            return
        errembed = discord.Embed(
            title="An error occurred.",
            description=str(exception),
            color=0xAA0000
        )
        await ctx.send(embed=errembed)



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
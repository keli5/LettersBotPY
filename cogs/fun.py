from discord.ext import commands
from scipy.io import wavfile
from classes.dbmodels import LBUser
from gtts import gTTS
import utility.funcs as f
import numpy
import random
import html
import requests  # i know this is blocking, but that's intended
import asyncio
import secrets
import json
import discord
from io import BytesIO
coin = ["heads", "tails", "side"]
weights = [50, 50, 0.00001]
noun = ["cat", "dog", "friend", "closest friend", "TV", "computer", "phone", "bed", "wall", "doorknob", "liver",
        "toes", "fingers", "legs"]
verb = ["stomp", "ignite", "eviscerate", "disappear", "compress", "stretch", "destroy", "steal", "pour water on"]


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cur = "֏"

    @commands.command(aliases=["image2audio", "imagetowav"])
    async def image2wav(self, ctx, attachment=None):
        """ Pipe the raw bytes from an image into a .wav file. """
        source = attachment or ctx.message.attachments[0].url or None
        image = await f.image_from_url(source)
        imgbytes = f.image_to_byte_array(image)
        samplingrate = 7000
        pcsmsg = await ctx.send('Processing... this may take a few minutes')
        async with ctx.channel.typing():
            buffer = BytesIO()
            bytes = numpy.array(imgbytes, dtype=numpy.int8)  # we'll feed this to our wav file
            wavfile.write(buffer, samplingrate, bytes)  # this is a bad idea
            filename = f"img2audio-{secrets.token_hex(nbytes=15)}.wav"  # generate a unique filename
            await ctx.send(file=discord.File(fp=buffer, filename=filename))
            await pcsmsg.delete()

    @commands.command(aliases=["coin", "cointoss"])
    async def coinflip(self, ctx):
        """ Flip a coin. """
        result = random.choices(coin, weights=weights, k=1)
        result = result[0]
        coinembed = discord.Embed(
            title=f"Flipped a coin and got {result}!"
        )
        coinembed.color = discord.Color.green()
        if result == "side":
            coinembed.color = discord.Color.red()
            coinembed.title = "Flipped a coin and got--"
            coinembed.description = "❌ The coin landed on its side"
        await ctx.send(embed=coinembed)

    @commands.command(aliases=["thiscatdoesnotexist"])
    async def aicat(self, ctx):
        """ Gets a cat that doesn't exist.

        Pull a fake cat from thiscatdoesnotexist.com. Some of them are good, and some of them.. aren't.
        """
        aicembed = discord.Embed(
            title="Fake cat  😳",
            color=discord.Color.greyple()
        )
        iid = random.randint(1, 6000000000)
        aicembed.set_image(url=f"https://thiscatdoesnotexist.com/?{iid}")
        aicembed.set_footer(text="Retrieved from thiscatdoesnotexist.com")
        await ctx.send(embed=aicembed)

    @commands.command()
    async def insult(self, ctx):
        """ Generate an... interesting insult. """
        v = random.choice(verb)
        n = random.choice(noun)
        end = random.choice(["!", "."])
        await ctx.send(f"I will {v} your {n}{end}")

    @commands.command(aliases=["roll"])
    async def diceroll(self, ctx, amount: int = 1, sides: int = 6):
        """ Roll some dice. """
        if amount > 50:
            return await ctx.send("You cannot roll more than 50 dice at a time.")
        if sides > 100:
            return await ctx.send("You cannot roll a dice with more than 100 sides.")
        roll = 0
        for i in range(amount):
            roll += random.randint(1, sides)
        await ctx.send(f"Rolled {amount}d{sides} and got {roll}.")

    @commands.command(aliases=["mkv"])
    async def markov(self, ctx, start: str = None):
        """ Generate a Markov chain. """
        start = start or None
        await ctx.send(f.call_markov(1600, start))

    @commands.command()
    async def trivia(self, ctx):
        """ Trivia question. Occasionally worth some money. """
        earn = 0
        if random.choice([True, False, False, False]):
            earn = random.randint(10, 50)
        q = json.loads(requests.get("https://opentdb.com/api.php?amount=1").content)["results"][0]
        category = q["category"]
        tembed = discord.Embed(
            title=f"Category: {category}",
            color=discord.Color.greyple()
        )
        answers = q["incorrect_answers"]
        letters = ["A", "B", "C", "D"]
        reacts = ["🇦", "🇧", "🇨", "🇩"]
        answers.append(q["correct_answer"])
        random.shuffle(answers)
        tembed.description = html.unescape(q["question"])
        if earn != 0:
            tembed.description += f"\nThis question is worth **{self.cur}{earn}!**"
        idx = 0
        correct_letter = None
        for answer in answers:
            idx += 1
            tembed.add_field(name=letters[idx - 1], value=html.unescape(answer))
            if answer == q["correct_answer"]:
                correct_letter = reacts[idx - 1]

        qmsg = await ctx.send(embed=tembed)
        for i in range(idx):
            await qmsg.add_reaction(reacts[i])
        await asyncio.sleep(15)
        qmsg = await ctx.fetch_message(qmsg.id)
        cor = q["correct_answer"]
        winners = []
        for reaction in qmsg.reactions:
            winnerpings = []
            if reaction.emoji == correct_letter:
                winners = await reaction.users().flatten()
                winners = winners[1:]
                if not winners:
                    return await ctx.send(embed=discord.Embed(
                        title=f"Nobody got it right! The answer was {cor}.",
                        color=discord.Color.red()
                    ))
            if reaction.emoji != correct_letter:
                losers = await reaction.users().flatten()
                for u in losers:
                    if u in winners:
                        winners.remove(u)
            for u in winners:
                winnerpings.append(u.mention)
                winnerdb = await f.db_for_user(u.id, True)
                mybal = winnerdb.balance
                await LBUser.filter(id=u.id).update(balance=mybal + earn)
            winnerpings = f.enumerate_list(winnerpings, 30)
        winnerembed = discord.Embed(
            title="Winners",
            color=discord.Color.green()
        )
        winnerembed.description = f"Congratulations to {winnerpings}! The answer was {cor}."
        if earn != 0:
            winnerembed.description += f"\nYou all earned {self.cur}{earn}!"
            winnerembed.description += f"\nCheck your balance with {self.bot.command_prefix}bal."
        await ctx.send(embed=winnerembed)

    @commands.command()
    async def spotify(self, ctx, user: discord.Member = None):
        """ See a user's Spotify information. Uses presences, so offline users / non-connected Spotify won't work. """
        user = user or ctx.author
        sembed = discord.Embed(
            title=f"Spotify for {user}"
        )
        spotify = None
        for activity in user.activities:
            if str(activity) == "Spotify":
                spotify = activity
        if not spotify:
            sembed.color = discord.Color.red()
            sembed.description = f"{user} is not listening to Spotify."
        else:
            sembed.color = spotify.color
            sembed.add_field(
                             name="Title",
                             value=f"[{spotify.title}](https://open.spotify.com/track/{spotify.track_id})",
                             inline=False
                            )
            sembed.add_field(name="Artists", value=f.enumerate_list(spotify.artists, 3), inline=False)
            sembed.add_field(name="Album", value=spotify.album)
            sembed.set_thumbnail(url=spotify.album_cover_url)

        await ctx.send(embed=sembed)

    @commands.command(aliases=["gtts"])
    async def tts(self, ctx, *, text):
        """ Reads out some text with the same voice as Google Translate. """
        out = BytesIO()
        processing = await ctx.send("Processing...")
        gTTS(text=text).write_to_fp(out)
        out.seek(0)
        await processing.delete()
        await ctx.send(file=discord.File(out, filename="tts.mp3"))


def setup(bot):
    bot.add_cog(Fun(bot))

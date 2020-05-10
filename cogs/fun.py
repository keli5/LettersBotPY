from discord.ext import commands
from scipy.io import wavfile
import numpy
import random
import secrets
from utility.funcs import image_to_byte_array, image_from_url, call_markov, enumerate_list
import discord
from io import BytesIO
coin = ["heads", "tails", "side"]
weights = [50, 50, 0.00001]


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["image2audio", "imagetowav"])
    async def image2wav(self, ctx, attachment=None):
        """ Pipe the raw bytes from an image into a .wav file. """
        source = attachment or ctx.message.attachments[0].url or None
        image = await image_from_url(source)
        imgbytes = image_to_byte_array(image)
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
    async def markov(self, ctx, length: int = 600):
        """ Generate a Markov chain. """
        if length > 1000:
            return await ctx.send("Max markov length is 1,000 characters.")
        await ctx.send(call_markov(length))

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
            sembed.add_field(name="Artists", value=enumerate_list(spotify.artists, 3))
            sembed.add_field(name="Album", value=spotify.album)
            sembed.set_thumbnail(url=spotify.album_cover_url)

        await ctx.send(embed=sembed)


def setup(bot):
    bot.add_cog(Fun(bot))

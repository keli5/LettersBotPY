from discord.ext import commands
from scipy.io import wavfile
import numpy
import secrets
from utility.funcs import image_to_byte_array, image_from_url
import discord
from io import BytesIO


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["image2audio", "imagetowav"])
    async def image2wav(self, ctx, attachment=None):
        source = attachment or ctx.message.attachments[0].url or None
        image = await image_from_url(source)
        imgbytes = image_to_byte_array(image)
        samplingrate = 7000
        pcsmsg = await ctx.send('Processing... this may take a few minutes')
        buffer = BytesIO()
        bytes = numpy.array(imgbytes, dtype=numpy.int8)  # we'll feed this to our wav file
        wavfile.write(buffer, samplingrate, bytes)  # this is a bad idea
        filename = f"img2audio-{secrets.token_hex(nbytes=15)}.wav"  # generate a unique filename
        await ctx.send(file=discord.File(fp=buffer, filename=filename))
        await pcsmsg.delete()


def setup(bot):
    bot.add_cog(Fun(bot))

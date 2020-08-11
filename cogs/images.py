import io
from PIL import ImageEnhance
from utility.funcs import image_from_url, image_to_byte_array
from scipy.io import wavfile
from discord.ext import commands
import discord
import numpy
import secrets

imagetypes = {
    "RGBA": "RGB with Transparency",
    "L": "Grayscale",
    "P": "8 bit color"
}


def __init__(self, bot):
    self.bot = bot


class Images(commands.Cog):

    @commands.command(aliases=["grayscale"])
    async def greyscale(self, ctx, attachment=None):  # Thank you Kaylynn!
        """Convert an image to greyscale (Luminance) mode. No transparency."""
        source = attachment or ctx.message.attachments[0].url or None
        out = io.BytesIO()
        im = await image_from_url(source)
        im = im.convert("RGB")  # intermediate just in case
        im = im.convert("L")
        im.save(out, "png")
        out.seek(0)
        await ctx.send(file=discord.File(out, filename="grayscale.png"))

    @commands.command(aliases=["image2audio", "imagetowav"])
    async def image2wav(self, ctx, attachment=None):
        """ Pipe the raw bytes from an image into a .wav file. """
        source = attachment or ctx.message.attachments[0].url or None
        image = await image_from_url(source)
        imgbytes = image_to_byte_array(image)
        samplingrate = 7000
        pcsmsg = await ctx.send('Processing... this may take a few minutes')
        async with ctx.channel.typing():
            buffer = io.BytesIO()
            bytes = numpy.array(imgbytes, dtype=numpy.int8)  # we'll feed this to our wav file
            wavfile.write(buffer, samplingrate, bytes)  # this is a bad idea
            filename = f"img2audio-{secrets.token_hex(nbytes=15)}.wav"  # generate a unique filename
            await ctx.send(file=discord.File(fp=buffer, filename=filename))
            await pcsmsg.delete()

    @commands.command(aliases=["colors"])
    async def resample(self, ctx, colors: int = 32, attachment=None):
        """ Sample an image down to <colors> colors. """
        if colors > 255:
            return await ctx.send('Maximum 255 colors.')
        source = attachment or ctx.message.attachments[0].url or None
        out = io.BytesIO()
        image = await image_from_url(source)
        processing = await ctx.send('Processing image... (this could take a bit)')
        async with ctx.channel.typing():
            width, height = image.size
            image = image.quantize(colors=colors, kmeans=colors)
            image = image.convert("RGB")
            hexcodes = b""
            for o, (r, g, b) in image.getcolors():
                hexcodes += b'#%02x%02x%02x\n' % (r, g, b)
            hexes = io.BytesIO(hexcodes)
            image.save(out, "png")
            out.seek(0)
            await processing.delete()
            await ctx.send(files=[
                discord.File(out, filename=f"{colors}-colors.png"),
                discord.File(hexes, filename="colors.txt")
                ]
            )

    @commands.command()
    async def saturate(self, ctx, amount: int = 2, attachment=None):
        """ Saturate an image. There's no limit, so this can easily wreck an image. """
        source = attachment or ctx.message.attachments[0].url or None
        out = io.BytesIO()
        image = await image_from_url(source)
        image = image.convert("RGBA")  # make sure we can color shift it
        image = ImageEnhance.Color(image).enhance(amount)
        image.save(out, "png")
        out.seek(0)
        await ctx.send(file=discord.File(out, filename="saturated.png"))

    @commands.command()
    async def imageinfo(self, ctx, attachment=None):
        """ Gets information about a provided image. """
        source = attachment or ctx.message.attachments[0].url or None
        image = await image_from_url(source)
        filename, ext = (source.split('/')[-1].split('.'))  # https://stackoverflow.com/a/25913757/
        filename = filename + "." + ext
        filename = filename.split("?")[0]
        iiembed = discord.Embed(
            title="Image information"
        )
        iiembed.set_thumbnail(url=source)
        iiembed.add_field(name="Filename", value=f"{filename}", inline=False if len(filename) > 16 else True)
        iiembed.add_field(name="Format", value=image.format)
        try:
            mode = imagetypes[image.mode]
        except BaseException:
            mode = image.mode
        try:
            animated = image.is_animated
        except BaseException:
            animated = False
        iiembed.add_field(name="Color mode", value=mode)
        iiembed.add_field(name="Resolution", value=f"{image.size[0]} \u00d7 {image.size[1]}")
        iiembed.add_field(name="Animated", value="Yes" if animated else "No")

        await ctx.send(embed=iiembed)


def setup(bot):
    bot.add_cog(Images(bot))

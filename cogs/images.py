from PIL import Image
import requests # lol watch this
import io
from utility.funcs import image_from_url ## todo - why does this not import?..
from discord.ext import commands
import discord
imagetypes = {
    "RGBA": "RGB with Transparency",
    "L": "Grayscale"
}


def __init__(self, bot):
    self.bot = bot

class Images(commands.Cog):

    @commands.command(aliases=["grayscale"])
    async def greyscale(self, ctx, attachment = None): # Thank you Kaylynn!
        """ Convert an image to greyscale (Luminance) mode. """
        source = attachment or ctx.message.attachments[0].url or None
        out = io.BytesIO()
        im = await image_from_url(source)
        im = im.convert("RGB")  # intermediate just in case
        im = im.convert("L")
        im.save(out, "png")
        out.seek(0)
        await ctx.send(file=discord.File(out, filename=f"grayscale.png"))
    
    @commands.command()
    async def imageinfo(self, ctx, attachment = None):
        source = attachment or ctx.message.attachments[0].url or None
        image = image_from_url(source)
        filename, ext = (source.split('/')[-1].split('.'))  # https://stackoverflow.com/a/25913757/
        iiembed = discord.Embed(
            title=f"Image info for {filename}.{ext}"
        )
        await ctx.send(embed=iiembed)


def setup(bot):
    bot.add_cog(Images(bot))

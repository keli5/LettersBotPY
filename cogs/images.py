from PIL import Image, ImageSequence
import io
from utility.funcs import image_from_url
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
        """ Convert an image to greyscale (Luminance) mode. No transparency. """
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
        image = await image_from_url(source)
        filename, ext = (source.split('/')[-1].split('.'))  # https://stackoverflow.com/a/25913757/
        filename = filename + "." + ext
        filename = filename.split("?")[0]
        iiembed = discord.Embed(
            title=f"Image information"
        )
        iiembed.add_field(name="Filename", value=f"{filename}", inline=False if len(filename) > 16 else True)
        iiembed.add_field(name="Format", value=image.format)
        try:
            mode = imagetypes[image.mode]
        except:
            mode = image.mode
        iiembed.add_field(name="Color mode", value=mode)
        iiembed.add_field(name="Resolution", value=f"{image.size[0]} \u00d7 {image.size[1]}")
        iiembed.add_field(name="Animated", value="Yes" if image.is_animated else "No")

        await ctx.send(embed=iiembed)


def setup(bot):
    bot.add_cog(Images(bot))

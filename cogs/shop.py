import discord
from discord.ext import commands
from classes.dbmodels import GuildShop
from utility.funcs import paginate_list


async def get_shop(id):
    try:
        shop = await GuildShop[id]
    except KeyError:
        shop = await GuildShop.create(
            id=id,
            items={}
        )
    return shop


class Shop(commands.Cog):
    # TODO: Add shop cog to load list when this is in working order.
    # Here goes nothing.
    def __init__(self, bot):
        self.bot = bot
        self.cur = "֏"

    @commands.group(invoke_without_command=True)
    async def shop(self, ctx, page: int = 1):
        """ Display the shop. """
        items = []
        prices = []
        shop = await get_shop(ctx.guild.id)
        shopembed = discord.Embed(
            title="Shop",
            description=f"Items for **`{ctx.guild.name}`**",
            color=discord.Color.greyple()
        )
        for item, price in shop.items.items():
            items.append(item)
            prices.append(price)

        prices = paginate_list(prices, 10, page)
        items = paginate_list(items, 10, page)  # uh, this is a bit of a hack.

        for item, price in zip(items, prices):
            shopembed.add_field(name=item, value=price)

        await ctx.send(embed=shopembed)

    @shop.command()
    async def buy(self, ctx, item: str):
        """ Buy an item from the shop. """
        items = await get_shop(ctx.guild.id).items
        try:
            obj = items[item]
        except KeyError:
            await ctx.send("That item is not in the shop.")
            return




def setup(bot):
    bot.add_cog(Shop(bot))

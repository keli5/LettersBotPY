import discord
from discord.ext import commands
from classes.dbmodels import GuildShop, LBUser
from utility.funcs import paginate_list, db_for_user


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
        if len(items) == 0:
            shopembed.description = "No items to display."
        for item, price in zip(items, prices):
            shopembed.add_field(name=item, value=self.cur + str(price))

        await ctx.send(embed=shopembed)

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx, page: int = 1, user: discord.User = None):
        """ Show your or another player's inventory. """
        items = []
        amounts = []
        user = user or ctx.author
        userdb = await db_for_user(user.id, True)
        shopembed = discord.Embed(
            title=f"Inventory of {ctx.author.name}",
            color=discord.Color.greyple()
        )
        for item, amount in userdb.inventory.items():
            items.append(item)
            amounts.append(amount)

        amounts = paginate_list(amounts, 10, page)
        items = paginate_list(items, 10, page)
        if len(items) == 0:
            shopembed.description = "No items to display."
        for item, amount in zip(items, amounts):
            shopembed.add_field(name=item, value=amount)

        await ctx.send(embed=shopembed)

    @shop.command()
    async def buy(self, ctx, item: str, amount: int = 1):
        """ Buy an item from the shop. """
        if amount < 1:
            return await ctx.send("You can't buy less than 1 item.")
        shop = await get_shop(ctx.guild.id)
        user = await db_for_user(ctx.author.id, True)
        user_inv = user.inventory
        await ctx.send(user_inv)

        items = shop.items
        try:
            price = items[item]
        except KeyError:
            return await ctx.send(f"{item if len(item) <= 55 else 'That item'} is not in the shop.")
        if price * amount > user.balance:
            return await ctx.send(f"You do not have enough money to buy {amount} {item}.")

        try:
            user_inv[item] += amount
        except KeyError:
            user_inv[item] = amount

        await LBUser.filter(id=ctx.author.id).update(balance=user.balance - (price * amount),
                                                     inventory=user_inv)
        buyembed = discord.Embed(
            title="Transaction successful!",
            description=f"You have bought {amount} {item} for {self.cur}{price * amount}.",
            color=discord.Color.green()
        )
        buyembed.add_field(name="Balance remaining", value=self.cur + str(user.balance - (price * amount)))
        await ctx.send(embed=buyembed)


def setup(bot):
    bot.add_cog(Shop(bot))

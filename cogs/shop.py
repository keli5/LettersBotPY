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

    @shop.command()
    async def sell(self, ctx, item: str, amount: int = 1):
        """ Sell an item to the shop. """
        if amount < 1:
            return await ctx.send("You can't sell less than 1 item.")
        shop = await get_shop(ctx.guild.id)
        user = await db_for_user(ctx.author.id, True)
        user_inv = user.inventory

        items = shop.items
        try:
            price = items[item]
        except KeyError:
            return await ctx.send(f"{item if len(item) <= 55 else 'That item'} is not in the shop.")
        if amount > user_inv[item]:
            return await ctx.send(f"You do not have enough {item} to sell.")

        try:
            user_inv[item] -= amount
        except KeyError:
            return await ctx.send(f"You do not have any {item} to sell.")

        await LBUser.filter(id=ctx.author.id).update(balance=user.balance + (price * amount),
                                                     inventory=user_inv)
        buyembed = discord.Embed(
            title="Transaction successful!",
            description=f"You have sold {amount} {item} for {self.cur}{price * amount}.",
            color=discord.Color.green()
        )
        buyembed.add_field(name="Balance remaining", value=self.cur + str(user.balance + (price * amount)))
        await ctx.send(embed=buyembed)

    @commands.command()
    async def give(self, ctx, user: discord.User, item: str, amount: int = 1):
        """Give an item to another user."""
        if amount < 1:
            return await ctx.send("You can't give less than 1 item.")
        sender = await db_for_user(ctx.author.id, True)
        receiver = await db_for_user(user.id, True)
        sender_inv = sender.inventory
        reciever_inv = receiver.inventory

        try:
            reciever_inv[item] += amount
        except KeyError:
            reciever_inv[item] = amount

        try:
            sender_inv[item] -= amount
        except KeyError:
            return await ctx.send(f"You do not have any {item} to give.")

        await LBUser.filter(id=ctx.author.id).update(inventory=sender_inv)
        await LBUser.filter(id=user.id).update(inventory=reciever_inv)
        giveembed = discord.Embed(
            title="Transaction successful!",
            description=f"You have given {amount} {item} to {user.name}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=giveembed)

    @commands.has_guild_permissions(manage_channels=True)
    @shop.command()
    async def additem(self, ctx, item: str, price: int):
        """ Add an item to the shop. """
        if (price < 0.05):
            return await ctx.send("Item must cost at least 0.05")
        shop = await get_shop(ctx.guild.id)
        shop.items[item] = price
        await GuildShop.filter(id=ctx.guild.id).update(items=shop.items)
        await ctx.send(f"{item} has been added to the shop, costs {self.cur}{price}")

    @commands.has_guild_permissions(manage_channels=True)
    @shop.command()
    async def removeitem(self, ctx, item: str):
        """ Remove an item from the shop. """
        shop = await get_shop(ctx.guild.id)

        try:
            del shop.items[item]
        except KeyError:
            return await ctx.send(f"{item} is not in the shop.")
        await GuildShop.filter(id=ctx.guild.id).update(items=shop.items)
        await ctx.send(f"{item} has been removed from the shop.")


def setup(bot):
    bot.add_cog(Shop(bot))

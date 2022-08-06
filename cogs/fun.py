from diskord.ext import commands
from diskord.ext.commands.cooldowns import BucketType
from classes.dbmodels import LBUser
from gtts import gTTS
import asyncio
import humanize
import datetime as dt
import utility.funcs as f
import utility.gameutils.blackjack as bj
import random
import html
import requests
import json
import diskord
from io import BytesIO
coin = ["heads", "tails"]
noun = ["cat", "dog", "friend", "closest friend", "TV", "computer", "phone", "bed", "wall", "doorknob", "liver",
        "toes", "fingers", "legs"]
verb = ["stomp", "ignite", "eviscerate", "disappear", "compress", "stretch", "destroy", "steal", "pour water on"]
hands = {}
dealer_hands = {}
decks = {}
bets = {}
active_game = {}
active_game_bot = {}


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = bot.command_prefix
        self.cur = "֏"

    @commands.command()
    @commands.cooldown(1, 45, BucketType.user)
    async def wheel(self, ctx, wager: float):
        """ Spin the wheel. You can lose your bet, or double it completely. """
        userdb = await f.db_for_user(ctx.author.id, True)
        if userdb.balance <= 0 or userdb.balance < wager:
            raise Exception("You can't afford that wager.")
        if wager > 50000:
            raise Exception("Maximum wager is 50,000.")
        if wager < 5:
            raise Exception("Can't bet less than 5")

        LBUser.filter(id=ctx.author.id).update(balance=userdb.balance - wager)
        wheelembed = diskord.Embed(
            title="Spin the Wheel!",
            color=diskord.Color.magenta()
        )
        msg = await ctx.send(embed=wheelembed)
        wheelembed.description = "Spinning..."
        await msg.edit(embed=wheelembed)
        multiplier = 1
        await asyncio.sleep(random.randint(10, 30)/10)
        multiplier = round(random.randint(0, 200) / 100, 2)
        wheelembed.title = f"You got {multiplier}x your bet."
        winnings = round(wager * multiplier, 2)
        text = ""
        if winnings - wager > 0:
            text = "won"
            wheelembed.color = diskord.Color.green()
        elif winnings - wager < 0:
            text = "lost"
            wheelembed.color = diskord.Color.red()
        else:
            text = "got"
            wheelembed.color = diskord.Color.greyple()
        fmoney = abs(round(winnings - wager, 2))
        fmoney = f"{fmoney:,}"
        wheelembed.description = f"You {text} {self.cur}{fmoney}."
        await msg.edit(embed=wheelembed)
        await LBUser.filter(id=ctx.author.id).update(balance=userdb.balance + winnings - wager)

    @commands.command(aliases=["coin", "cointoss"])
    async def coinflip(self, ctx):
        """ Flip a coin. """
        result = random.choice(coin)
        result = result[0]
        coinembed = diskord.Embed(
            title=f"Flipped a coin and got {result}!"
        )
        coinembed.color = diskord.Color.green()
        if result == "side":
            coinembed.color = diskord.Color.red()
            coinembed.title = "Flipped a coin and got..."
            coinembed.description = "...the coin landed on its side?"
        await ctx.send(embed=coinembed)

    @commands.command(aliases=["roll"])
    async def diceroll(self, ctx, amount: int = 1, sides: int = 6, modifier: int = 0):
        """ Roll some dice. """
        if amount > 50 or amount < 1:
            return await ctx.send("You cannot roll more than 50 or less than 1 dice at a time.")
        if sides > 100 or sides < 2:
            return await ctx.send("You cannot roll a dice with more than 100 or less than 2 sides.")
        roll = 0
        rolls = []
        mod = ""
        for i in range(amount):
            rolled = random.randint(1, sides)
            roll += rolled
            rolls.append(str(rolled))

        if modifier > 0:
            mod = f"+{modifier}"
        elif modifier < 0:
            mod = modifier
        else:
            mod = ""

        modtext = mod or "no modifier"  # FUCK
        rolls = " + ".join(rolls)
        await ctx.send(f"Rolled `{amount}d{sides}{mod}`.\n{rolls} with {modtext} = {roll+modifier}.")

    @commands.command(aliases=["mkv"])
    async def markov(self, ctx, start: str = None):
        """ Generate a Markov chain. """
        try:
            await ctx.send(f.call_markov(1600, start.lower()))
        except Exception as e:
            if "can't find sentence" in str(e):
                return await ctx.send(f"`{start}` does not appear enough in the corpus.")
            if "requires a string containing" in str(e):
                return await ctx.send(f"`{start}` has too many words. (max 2)")

    @commands.command()
    async def trivia(self, ctx):
        """ Trivia question. Occasionally worth some money. """
        earn = 0
        if random.choice([True, False, False, False]):
            earn = random.randint(10, 50)
        q = json.loads(requests.get("https://opentdb.com/api.php?amount=1").content)["results"][0]
        category = q["category"]
        tembed = diskord.Embed(
            title=f"Category: {category}",
            color=diskord.Color.greyple()
        )
        answers = q["incorrect_answers"]
        letters = ["A", "B", "C", "D"]
        reacts = ["🇦", "🇧", "🇨", "🇩"]
        answers.append(q["correct_answer"])
        random.shuffle(answers)
        if len(answers) == 2 and answers[1] == "True":
            answers.reverse()
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
                    return await ctx.send(embed=diskord.Embed(
                        title=f"Nobody got it right! The answer was {cor}.",
                        color=diskord.Color.red()
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
        winnerembed = diskord.Embed(
            title="Winners",
            color=diskord.Color.green()
        )
        winnerembed.description = f"Congratulations to {winnerpings}! The answer was {html.unescape(cor)}."
        if earn != 0:
            winnerembed.description += f"\nYou all earned {self.cur}{earn}!"
            winnerembed.description += f"\nCheck your balance with {self.bot.command_prefix}bal."
        await ctx.send(embed=winnerembed)

    @commands.command()
    async def spotify(self, ctx, user: diskord.Member = None):
        """ See a user's Spotify information. Uses presences, so offline users / non-connected Spotify won't work.
        It's real fucky, especially on mobile.  """
        user = user or ctx.author
        sembed = diskord.Embed(
            title=f"Spotify for {user}"
        )
        spotify = None
        for activity in user.activities:
            if str(activity) == "Spotify":
                spotify = activity
        if not spotify:
            sembed.color = diskord.Color.red()
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
        await ctx.send(file=diskord.File(out, filename="tts.mp3"))

    @commands.group(invoke_without_command=True, aliases=["scramble"])
    async def shuffle(self, ctx, *, string):
        """ Randomly scramble a string of words. """
        s = string.split(" ")
        random.shuffle(s)
        await ctx.send(" ".join(s))

    @shuffle.command(aliases=["char"])
    async def character(self, ctx, *, string):
        """ Less coherent version of shuffle. Splits by character. """
        s = list(string)
        random.shuffle(s)
        await ctx.send("".join(s))

    @commands.command()
    async def xkcd(self, ctx, num: int = 0):
        cembed = diskord.Embed()
        comic = num
        if num == 0:
            comic = ""
        response = requests.get(f"https://xkcd.com/{comic}/info.0.json")
        if response.status_code == 404:
            cembed.title = f"Couldn't find comic #{num}"
            cembed.color = 0xFF0000
            cembed.set_footer(text="Check the number, or provide none for the latest comic.")
            return await ctx.send(embed=cembed)
        res_json = json.loads(response.content)

        year = int(res_json["year"])
        month = int(res_json["month"])
        day = int(res_json["day"])

        cdate = humanize.naturaldate(dt.date(year, month, day))
        cembed.set_image(url=res_json["img"])  # I hate the below line, but better than f-strings for this use
        cembed.title = "{} (#{})".format(res_json["safe_title"], res_json["num"])
        cembed.description = res_json["alt"]
        cembed.set_footer(text=cdate.capitalize())
        await ctx.send(embed=cembed)

    @commands.command(name="8ball")
    async def magic8ball(self, ctx, *, question):
        m8embed = diskord.Embed(
            title="🎱 Magic 8 ball",
            color=diskord.Color.greyple()
        )
        m8embed.add_field(name="❓ Question", value=question)
        m8embed.add_field(name="🎱 Answer", value=f.super_secret_8ball())
        await ctx.send(embed=m8embed)

    @commands.command(aliases=["bj"])
    @commands.is_owner()
    async def blackjack(self, ctx, wager: int):
        """ Blackjack! Maximum wager 7500 """
        # here goes nothing
        user_db = await f.db_for_user(ctx.author.id, True)
        bal = user_db.balance
        if wager > bal:
            raise Exception("You can't afford that wager.")
        if wager > 7500:
            raise Exception("Maximum wager is 7500.")
        if wager < 15:
            raise Exception("Minimum wager is 15.")
        if active_game.get(ctx.author.id):  # wok made dude shit himself :sob:
            raise Exception("You already have a game in progress. Finish that first.")
        print("Money")
        # This shit is a little bit of a mess
        decks[ctx.author.id] = bj.new_deck()
        deck = decks[ctx.author.id]
        active_game[ctx.author.id] = ctx.message

        hands[ctx.author.id] = [bj.deal(deck), bj.deal(deck)]
        dealer_hands[ctx.author.id] = [bj.deal(deck), bj.deal(deck)]
        print("Variables")
        dealer_hands[ctx.author.id][1].hidden = True  # lol, horrorcode
        bets[ctx.author.id] = wager
        await LBUser.filter(id=ctx.author.id).update(balance=user_db.balance - wager)

        # did we already win? trick question: you're programming, you never win
        if bj.value(hands[ctx.author.id]) == 21:  # player got a blackjack
            winembed = diskord.Embed(
                    title="Blackjack!",
                    description=f"{ctx.author.mention} got 21!\n",
                    color=diskord.Color.green(),
            )
            winnings = bets[ctx.author.id] * 3.5
            winembed.add_field(name="Winnings", value=winnings)
            await LBUser.filter(id=ctx.author.id).update(balance=user_db.balance + winnings)
            active_game[ctx.author.id] = None
            active_game_bot[ctx.author.id] = None
            return await ctx.send(embed=winembed)

        readable_hand = [card.name for card in hands[ctx.author.id]]
        readable_dealer_hand = [card.name for card in dealer_hands[ctx.author.id]]
        active_game_bot[ctx.author.id] = await ctx.send(embed=diskord.Embed(
                title="Blackjack",
                description=f"Player's hand: {' | '.join(readable_hand)} (total {bj.value(hands[ctx.author.id])})\n" +
                f"Dealer's hand: {' | '.join(readable_dealer_hand)} (total {bj.value(dealer_hands[ctx.author.id])})",
            ).set_footer(text="🃏 HIT | 🖐️ STAND")
        )
        await active_game_bot[ctx.author.id].add_reaction("🃏")
        await active_game_bot[ctx.author.id].add_reaction("🖐️")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if active_game:
            player_stood = False
            if reaction.emoji == "🃏" and not player_stood and not user.bot:
                # hit
                hit = bj.player_hit(bj.deal(decks[user.id]), hands[user.id])

                if hit is True:  # explicitly check for true, it could be a truthy value
                    newtitle = "You got 21!"
                    await LBUser.filter(id=user.id).update(
                        balance=await f.db_for_user(user.id, True).balance + bets[user.id] * 2.5
                    )
                    active_game[user.id] = None
                    active_game_bot[user.id] = None  # clean up
                    return
                elif hit is False:
                    newtitle = "You busted!"

                readable_hand = [card.name for card in hands[user.id]]
                readable_dealer_hand = [card.name for card in dealer_hands[user.id]]
                await active_game_bot[user.id].edit(embed=diskord.Embed(
                    title=newtitle or "Blackjack",
                    description=f"Player's hand: {' | '.join(readable_hand)} (total {bj.value(hands[user.id])})\n" +
                    f"Dealer's hand: {' | '.join(readable_dealer_hand)} (total {bj.value(dealer_hands[user.id])})",
                ).set_footer(text="🃏 HIT | 🖐️ STAND"))

            if reaction.emoji == "🖐️":
                # user stands
                player_stood = True

            while bj.value(dealer_hands[user.id]) < 17:
                dealer_hands[user.id].append(bj.deal(decks[user.id]))
                readable_hand = [card.name for card in hands[user.id]]
                readable_dealer_hand = [card.name for card in dealer_hands[user.id]]

                await active_game_bot[user.id].edit(embed=diskord.Embed(
                    title=newtitle or "Blackjack",
                    description=f"Player's hand: {' | '.join(readable_hand)} (total {bj.value(hands[user.id])})\n" +
                    f"Dealer's hand: {' | '.join(readable_dealer_hand)} (total {bj.value(dealer_hands[user.id])})",
                ))

            if bj.value(dealer_hands[user.id]) > bj.value(hands[user.id]):
                newtitle = "Dealer wins!"
            if bj.value(dealer_hands[user.id]) < bj.value(hands[user.id]):
                newtitle = "You win!"
                await LBUser.filter(id=user.id).update(
                    balance=await f.db_for_user(user.id, True).balance + bets[user.id] * 1.65
                )
            if bj.value(dealer_hands[user.id]) == bj.value(hands[user.id]):
                newtitle = "Push!"
                await LBUser.filter(id=user.id).update(
                    balance=await f.db_for_user(user.id, True).balance + bets[user.id]
                )


def setup(bot):
    bot.add_cog(Fun(bot))

# lot of bullshit here
# it needs its own file
import random
from classes.dbmodels import LBUser
from utility.funcs import db_for_user
suits = ["<:spades:936447656463597568>", "<:hearts:936447656480350249>",
         "<:diamonds:936447656589398066>", "<:clubs:936447656199348256>"]
numbers = list(range(1, 10))
decks = {}
hands = {}


class Card:
    def __init__(self, suit, value, ace: bool = False, symbol=None, hidden=False):
        self.suit = suit
        self.value = value
        self.ace = ace
        self.symbol = symbol or str(value)
        self.name = str(symbol) + " " + suit
        self.hidden = hidden

        if self.hidden:
            self.name = "?? of ?"


def new_deck():
    """ Get a new 4 decks of cards """
    cards = []
    for _ in range(4):
        for suit in suits:
            for number in numbers:
                cards.append(Card(suit, number, False, number))
            cards.append(Card(suit, 11, True, "A"))
            cards.append(Card(suit, 10, False, "J"))
            cards.append(Card(suit, 10, False, "Q"))
            cards.append(Card(suit, 10, False, "K"))
    return cards


def deal(deck):
    """ Deal a card from the deck """
    return deck.pop(random.randint(0, len(deck) - 1))


def player_hit(card, player_hand):
    """ Player hit logic """
    player_hand_value = value(player_hand)
    if card.ace and (card.value + player_hand_value) > 21:
        player_hand.append(Card(card.suit, 1, True, "A"))
    else:
        player_hand.append(card)

    player_hand_value = value(player_hand)
    return player_hand


def dealer_play(card, dealer_hand):

    if card.ace and (card.value + value(dealer_hand)) > 21:
        dealer_hand.append(Card(card.suit, 1, True, "A"))
    else:
        dealer_hand.append(card)

    return dealer_hand


def dealer_finish(dealer_hand: list[Card], deck: list[Card]) -> list[Card]:
    # Finishes the dealers hand once the player has hit 21, busted or stood
    while value(dealer_hand) <= 16:
        dealer_hand = dealer_play(deal(deck), dealer_hand)
    return dealer_hand


def value(hand):
    """ Get the value of a hand """
    aces = []
    total = 0
    for card in hand:
        if card.hidden:
            continue
        if card.ace:
            aces.append(card)
            continue
        total += card.value
    if aces:
        if len(aces) == 1:
            if total+11 > 21:
                aces[0].value = 1
                return total + 1
            if total + 11 <= 21:
                aces[0].value = 11
                return total + 11

        if len(aces) > 2:
            # if we have 2 aces they both cant be 11 or can they *insert vasuce music*
            a = aces[0].value + (len(aces)-1) + total
            if a <= 21:
                aces.pop(0)
                for ace in aces:
                    ace.value = 1
                return 21
            if a > 21:
                if len(aces) + total > 21:
                    for ace in aces:
                        ace.value = 1
                    return total+len(aces)
                return a
    else:
        return total


async def update_bal(user_id: str, ammount):
    user = await db_for_user(user_id, True)
    await LBUser.filter(id=user_id).update(user.balance+ammount)


async def get_bal(user_id):
    user = await db_for_user(user_id, True)
    return user.balance


def value_with_hidden(hand: list[Card]):
    aces = []
    total = 0
    for card in hand:
        if card.ace:
            aces.append(card)
            continue
        total += card.value
    if aces:
        if len(aces) == 1:
            if total+11 > 21:
                aces[0].value = 1
                return total + 1
            if total + 11 <= 21:
                aces[0].value = 11
                return total+11

        if len(aces) > 2:
            # if we have 2 aces they both cant be 11 or can they *insert vasuce music*
            a = aces[0].value + (len(aces)-1) + total
            if a <= 21:
                aces.pop(0)
                for ace in aces:
                    ace.value = 1
                return 21
            if a > 21:
                if len(aces) + total > 21:
                    for ace in aces:
                        ace.value = 1
                    return total+len(aces)
                return a
    else:
        return total

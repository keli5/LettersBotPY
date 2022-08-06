# lot of bullshit here
# it needs its own file
import random

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

    if player_hand_value > 21:
        return False  # bust
    elif player_hand_value == 21:
        return True  # blackjack

    if card.ace and (card.value + player_hand_value) > 21:
        player_hand.append(Card(card.suit, 1, True, "A"))
    else:
        player_hand.append(card)

    player_hand_value = value(player_hand)
    return player_hand


def dealer_play(card, dealer_hand):

    if value(dealer_hand) > 21:
        return False  # dealer busted, player wins
    elif value(dealer_hand) == 21:
        return True  # dealer blackjack

    if card.ace and (card.value + value(dealer_hand)) > 21:
        dealer_hand.append(Card(card.suit, 1, True, "A"))
    else:
        dealer_hand.append(card)

    return dealer_hand


def value(hand):
    """ Get the value of a hand """
    total = 0
    for card in hand:
        total += card.value
    return total

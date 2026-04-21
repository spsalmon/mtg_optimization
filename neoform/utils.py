import random
from neoform.cards import CARD_TAGS

def parse_decklist(decklist_str: str) -> dict[str, int]:
    deck = {}
    for line in decklist_str.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 1)
        count = int(parts[0])
        name = parts[1]
        deck[name] = count
    return deck

def get_starting_hand(deck):
    return deck[:7]

def initialize_deck(deck_list):
    deck = []

    for key, value in deck_list.items():
        deck.extend([key]*value)

    random.shuffle(deck)
    deck_card_tags = [CARD_TAGS[card] for card in deck]

    full_deck = [(name, tags) for name, tags in zip(deck, deck_card_tags)]

    return full_deck

def get_card_names(card_list):
    return [card[0] for card in card_list]
from neoform.engine.mana import check_if_castable, get_missing_mana, pay_mana_cost
import numpy as np
import random
import copy

def draw(deck, n):
    drawn_cards = []
    for i in range(n):
        drawn_cards.append(deck.pop(0))

    return drawn_cards

def fetch(fetch_land, deck, missing_combo_pieces, missing_mana):
    missing_mana_count = [len(missing_mana) for missing_mana in missing_mana]
    missing_mana = sorted(missing_mana, key=lambda x: len(x))

    fetchable_types = fetch_land[1].can_fetch
    lands_with_types = [card for card in deck if card[1].land_type]
    fetchable_lands = [card for card in lands_with_types if np.any([land_type in fetchable_types for land_type in card[1].land_type])]

    untapped_lands = [land for land in fetchable_lands if land[1].untapped]
    untapped_duals = [land for land in untapped_lands if (land[1].produces_green and land[1].produces_blue)]
    untapped_green_source = [land for land in untapped_lands if land[1].produces_green]
    untapped_blue_source = [land for land in untapped_lands if land[1].produces_blue]
    surveil_lands = [land for land in fetchable_lands if land[1].surveil]

    if len(missing_mana_count) > 0 and np.min(missing_mana_count) == 1:
        pip = missing_mana[0]
        if untapped_duals:
            return untapped_duals[0]
        elif pip == "G":
            if untapped_green_source:
                return untapped_green_source[0]
            else:
                pass
        elif pip == "U":
            if untapped_blue_source:
                return untapped_blue_source[0]
            else:
                pass
        else:
            if untapped_blue_source:
                return untapped_blue_source[0]
            elif untapped_green_source:
                return untapped_green_source[0]
            else:
                pass

    if surveil_lands:
        return surveil_lands[0]
    else:
        if untapped_duals:
            return untapped_duals[0]
        if untapped_blue_source:
            return untapped_blue_source[0]
        elif untapped_green_source:
            return untapped_green_source[0]


def decide_surveil(deck, missing_sac_target, missing_sac_outlet, missing_mana, lands_in_hand, missing_green_cards, missing_cantrip):
    """
    Pure function: given the current game state, return 'keep' or 'bin' for the top card.
    Does NOT mutate anything.
    """
    card_on_top = deck[0]

    if len(missing_mana) > 0:
        missing_mana_count = np.min([len(m) for m in missing_mana])
    else:
        missing_mana_count = 0

    if missing_sac_outlet and card_on_top[1].sac_outlet:
        return "keep"
    elif missing_sac_target and card_on_top[1].sac_target:
        return "keep"
    elif missing_mana_count > len(lands_in_hand) and card_on_top[1].land:
        return "keep"
    elif missing_green_cards and card_on_top[1].green:
        return "keep"
    elif missing_cantrip and card_on_top[1].cantrip:
        return "keep"
    else:
        return "bin"

def surveil(deck, missing_sac_target, missing_sac_outlet, missing_mana, lands_in_hand, missing_green_cards, missing_cantrip):
    """
    Stateful wrapper: decides and applies the surveil decision in place.
    """
    decision = decide_surveil(deck, missing_sac_target, missing_sac_outlet, missing_mana, lands_in_hand, missing_green_cards, missing_cantrip)
    if decision == "bin":
        deck.pop(0)

def check_for_win(hand, mana_pool, deck):
    sac_targets = [card for card in hand if card[1].sac_target]
    sac_outlets = [card for card in hand if card[1].sac_outlet]

    green_cards = [card for card in hand if card[1].green]
    sac_outlet_castable = np.any([check_if_castable(sac_outlet, mana_pool) for sac_outlet in sac_outlets])
    sac_target_castable = (len(sac_targets) > 0) & (len(green_cards) >= 4)
    win = sac_outlet_castable & sac_target_castable

    missing_mana_to_cast_sac_outlet = [get_missing_mana(sac_outlet, mana_pool) for sac_outlet in sac_outlets]

    if not missing_mana_to_cast_sac_outlet:
        sac_outlets_in_deck = [card for card in deck if card[1].sac_outlet]
        sac_outlets_in_deck = list(set(sac_outlets_in_deck))
        missing_mana_to_cast_sac_outlet = [get_missing_mana(sac_outlet, mana_pool) for sac_outlet in sac_outlets_in_deck]

    missing_sac_target = (len(sac_targets) == 0)
    missing_sac_outlet = (len(sac_outlets) == 0)
    missing_green_cards = len(green_cards) < 4

    if not win:
        return False, (missing_mana_to_cast_sac_outlet, missing_sac_target, missing_sac_outlet, missing_green_cards)
    else:
        return True, ([], False, False, False)

    
def check_for_cantrip(hand, mana_pool):
    cantrips = [card for card in hand if card[1].cantrip]
    cantrips = sorted(cantrips, key=lambda c: getattr(c[1], "cantrip_power", 0), reverse=True)
    missing_cantrip = len(cantrips) == 0
    castable_cantrips = [card for card in cantrips if check_if_castable(card, mana_pool)]
    missing_mana_to_cast_cantrip = [get_missing_mana(cantrip, mana_pool) for cantrip in cantrips]

    return castable_cantrips, missing_cantrip, missing_mana_to_cast_cantrip

    
def play_land(lands_in_hand, missing_mana):
    missing_mana = sorted(missing_mana, key=lambda x: len(x))
    untapped_lands_in_hand = [land for land in lands_in_hand if land[1].untapped]
    fetch_lands_in_hand = [land for land in lands_in_hand if land[1].fetch]
    untapped_duals = [land for land in untapped_lands_in_hand if (land[1].produces_green and land[1].produces_blue)]
    untapped_green_source = [land for land in untapped_lands_in_hand if land[1].produces_green and not land[1].green]
    untapped_blue_source = [land for land in untapped_lands_in_hand if land[1].produces_blue]
    surveil_lands_in_hand = [land for land in lands_in_hand if land[1].surveil]
    mdfc_lands_in_hand = [land for land in lands_in_hand if land[1].green and land[1].land]

    missing_mana_for_cheapest_spell = missing_mana[0] if len(missing_mana) > 0 else None
    if missing_mana_for_cheapest_spell is not None:
        for pip in missing_mana_for_cheapest_spell:
            if untapped_duals:
                return untapped_duals[0]
            elif pip == "G":
                if untapped_green_source:
                    return untapped_green_source[0]
                elif fetch_lands_in_hand:
                    return fetch_lands_in_hand[0]
                elif mdfc_lands_in_hand:
                    return mdfc_lands_in_hand[0]
                else:
                    pass
            elif pip == "U":
                if untapped_blue_source:
                    return untapped_blue_source[0]
                elif fetch_lands_in_hand:
                    return fetch_lands_in_hand[0]
                else:
                    pass
            else:
                if untapped_blue_source:
                    return untapped_blue_source[0]
                elif untapped_green_source:
                    return untapped_green_source[0]
                elif fetch_lands_in_hand:
                    return fetch_lands_in_hand[0]
                else:
                    pass
            
    if surveil_lands_in_hand:
        return surveil_lands_in_hand[0]
    elif fetch_lands_in_hand:
        return fetch_lands_in_hand[0]
    else:
        if untapped_green_source:
            return untapped_green_source[0]
        if untapped_blue_source:
            return untapped_blue_source[0]


def process_played_land(land, hand, battlefield, mana_pool, mana_pool_for_turn, lands_in_hand, deck, missing_sac_target, missing_sac_outlet, missing_green_cards, missing_mana, missing_cantrip):
    missing_combo_pieces = missing_green_cards or missing_sac_outlet or missing_sac_target
    if land is None:
        return
    hand.remove(land)
    if land[1].fetch:
        fetched_land = fetch(land, deck, missing_combo_pieces, missing_mana)
        if fetched_land is not None:
            deck.remove(fetched_land)
            random.shuffle(deck)
            battlefield.append(fetched_land)
        else:
            battlefield.append(land)
    else:
        battlefield.append(land)

    if getattr(battlefield[-1][1], "surveil", False):
        surveil(deck, missing_sac_target, missing_sac_outlet, missing_mana, lands_in_hand, missing_green_cards, missing_cantrip)

    land_production = []
    if getattr(battlefield[-1][1], "produces_green", False):
        land_production.append('G')
    if getattr(battlefield[-1][1], "produces_blue", False):
        land_production.append('U')
    if getattr(battlefield[-1][1], "untapped", False):
        mana_pool_for_turn.append(land_production)
    mana_pool.append(land_production)


def cantrip(card, mana_pool, hand, deck, missing_sac_target, missing_sac_outlet, missing_mana, lands_in_hand, missing_green_cards):
    cantrip_cost = card[1].cost
    mana_pool = pay_mana_cost(cantrip_cost, mana_pool)
    hand.remove(card)
    
    cantrip_pool = []
    
    for i in range(card[1].cantrip_power):
        cantrip_pool.append(deck.pop(0))

    sac_targets = [card for card in cantrip_pool if card[1].sac_target]
    sac_outlets = [card for card in cantrip_pool if card[1].sac_outlet]
    lands = [card for card in cantrip_pool if card[1].land]
    green_cards = [card for card in cantrip_pool if card[1].green]
    cantrips = [card for card in cantrip_pool if card[1].cantrip]

    sac_outlets = sorted(sac_outlets, key=lambda c: len(getattr(c[1], "cost", [])))
    cantrips = sorted(cantrips, key=lambda c: getattr(c[1], "cantrip_power", 0), reverse=True)

    card = None
    if missing_sac_target and len(sac_targets) > 0:
        card = sac_targets[0]
    elif missing_sac_outlet and len(sac_outlets) > 0:
        card = sac_outlets[0]
    elif missing_mana and len(lands) > 0:
        duals = [l for l in lands if getattr(l[1], "produces_green", False) and getattr(l[1], "produces_blue", False)]
        greens = [l for l in lands if getattr(l[1], "produces_green", False)]
        blues = [l for l in lands if getattr(l[1], "produces_blue", False)]
        if duals:
            card = duals[0]
        elif greens:
            card = greens[0]
        elif blues:
            card = blues[0]
        else:
            card = lands[0]
    elif missing_green_cards and len(green_cards) > 0:
        card = green_cards[0]
    elif len(cantrips) > 0:
        card = cantrips[0]
    else:
        card = cantrip_pool[0]

    hand.append(card)
    cantrip_pool.remove(card)
    for c in reversed(cantrip_pool):
        deck.insert(-1, c)
    
    return mana_pool


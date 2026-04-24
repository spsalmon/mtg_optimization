from neoform.engine.game_actions import draw, play_land, cantrip, check_for_win, check_for_cantrip, process_played_land
from neoform.utils import initialize_deck
import numpy as np
import copy

def simulate_game_no_mull(deck_list, turns_to_win = 10, on_the_play = True, starting_hand_size = 7):
    deck = initialize_deck(deck_list)
    hand = draw(deck, n=starting_hand_size)  # draw() returns a list of tuples, so hand is a list of tuples
    battlefield = []
    mana_pool = []

    starting_hand = hand.copy()

    for turn in range(1, turns_to_win+1):
        if turn != 1 or not on_the_play:
            # draw a card and extend the hand (don't append the list)
            drawn = draw(deck, 1)
            if drawn:
                hand.extend(drawn)

        mana_pool_for_turn = mana_pool.copy()
        land_drop_left = True
        
        lands_in_hand = [card for card in hand if card[1].land]
        
        win, (missing_mana_to_cast_sac_outlet, missing_sac_target, missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
        castable_cantrips, missing_cantrip, missing_mana_to_cast_cantrip = check_for_cantrip(hand, mana_pool_for_turn)
        
        if win:
            return turn, starting_hand
        
        missing_mana_count = [len(missing_mana) for missing_mana in missing_mana_to_cast_sac_outlet]

        if len(missing_mana_count) > 0 and (np.min(missing_mana_count) == 1) and lands_in_hand:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)
            process_played_land(
                land,
                hand,
                battlefield,
                mana_pool,
                mana_pool_for_turn,
                lands_in_hand,
                deck,
                missing_sac_target,
                missing_sac_outlet,
                missing_green_cards,
                missing_mana_to_cast_sac_outlet,
                missing_cantrip,
            )        

            win, (missing_mana_to_cast_sac_outlet, missing_sac_target, missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
            if win:
                return turn, starting_hand
            

        if len(castable_cantrips) > 0:
            mana_pool_for_turn = cantrip(
            castable_cantrips[0],
            mana_pool_for_turn,
            hand,
            deck,
            missing_sac_target,
            missing_sac_outlet,
            missing_mana_to_cast_sac_outlet,
            lands_in_hand,
            missing_green_cards,
            )

        missing_mana_count = [len(missing_mana) for missing_mana in missing_mana_to_cast_cantrip]

        if len(missing_mana_count) > 0 and (np.min(missing_mana_count) == 1) and lands_in_hand and land_drop_left:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)
            process_played_land(
                land,
                hand,
                battlefield,
                mana_pool,
                mana_pool_for_turn,
                lands_in_hand,
                deck,
                missing_sac_target,
                missing_sac_outlet,
                missing_green_cards,
                missing_mana_to_cast_cantrip,
                missing_cantrip,
            )
            castable_cantrips, missing_cantrip, missing_mana_to_cast_cantrip = check_for_cantrip(hand, mana_pool_for_turn)
            if len(castable_cantrips) > 0:
                mana_pool_for_turn = cantrip(
                castable_cantrips[0],
                mana_pool_for_turn,
                hand,
                deck,
                missing_sac_target,
                missing_sac_outlet,
                missing_mana_to_cast_sac_outlet,
                lands_in_hand,
                missing_green_cards,
                )


        # we do not want to cantrip with Planar Genesis if we're just missing green cards !!!

        # play a land if possible
        if lands_in_hand and land_drop_left:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)

            process_played_land(
                land,
                hand,
                battlefield,
                mana_pool,
                mana_pool_for_turn,
                lands_in_hand,
                deck,
                missing_sac_target,
                missing_sac_outlet,
                missing_green_cards,
                missing_mana_to_cast_sac_outlet,
                missing_cantrip,
            )

        win, (missing_mana_to_cast_sac_outlet, missing_sac_target, missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
        if win:
            return turn, starting_hand

    return None

def simulate_starting_hand(starting_hand, deck_list, turns_to_win = 10, on_the_play = True):
    deck = initialize_deck(deck_list)
    starting_hand = initialize_deck(starting_hand)

    hand = starting_hand.copy()  # hand is a list of tuples

    # remove the cards in the starting hand from the deck
    for card in starting_hand:
        deck.remove(card)

    battlefield = []
    mana_pool = []

    for turn in range(1, turns_to_win+1):
        if turn != 1 or not on_the_play:
            # draw a card and extend the hand (don't append the list)
            drawn = draw(deck, 1)
            if drawn:
                hand.extend(drawn)

        mana_pool_for_turn = mana_pool.copy()
        land_drop_left = True
        
        lands_in_hand = [card for card in hand if card[1].land]
        
        win, (missing_mana_to_cast_sac_outlet, missing_sac_target, missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
        castable_cantrips, missing_cantrip, missing_mana_to_cast_cantrip = check_for_cantrip(hand, mana_pool_for_turn)
        
        if win:
            return turn, starting_hand        
        missing_mana_count = [len(missing_mana) for missing_mana in missing_mana_to_cast_sac_outlet]

        if len(missing_mana_count) > 0 and (np.min(missing_mana_count) == 1) and lands_in_hand:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)
            process_played_land(
                land,
                hand,
                battlefield,
                mana_pool,
                mana_pool_for_turn,
                lands_in_hand,
                deck,
                missing_sac_target,
                missing_sac_outlet,
                missing_green_cards,
                missing_mana_to_cast_sac_outlet,
                missing_cantrip,
            )        

            win, (missing_mana_to_cast_sac_outlet, missing_sac_target, missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
            if win:
                return turn, starting_hand
            

        if len(castable_cantrips) > 0:
            mana_pool_for_turn = cantrip(
            castable_cantrips[0],
            mana_pool_for_turn,
            hand,
            deck,
            missing_sac_target,
            missing_sac_outlet,
            missing_mana_to_cast_sac_outlet,
            lands_in_hand,
            missing_green_cards,
            )

        missing_mana_count = [len(missing_mana) for missing_mana in missing_mana_to_cast_cantrip]

        if len(missing_mana_count) > 0 and (np.min(missing_mana_count) == 1) and lands_in_hand and land_drop_left:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)
            process_played_land(
                land,
                hand,
                battlefield,
                mana_pool,
                mana_pool_for_turn,
                lands_in_hand,
                deck,
                missing_sac_target,
                missing_sac_outlet,
                missing_green_cards,
                missing_mana_to_cast_cantrip,
                missing_cantrip,
            )
            castable_cantrips, missing_cantrip, missing_mana_to_cast_cantrip = check_for_cantrip(hand, mana_pool_for_turn)
            if len(castable_cantrips) > 0:
                mana_pool_for_turn = cantrip(
                castable_cantrips[0],
                mana_pool_for_turn,
                hand,
                deck,
                missing_sac_target,
                missing_sac_outlet,
                missing_mana_to_cast_sac_outlet,
                lands_in_hand,
                missing_green_cards,
                )

        # we do not want to cantrip with Planar Genesis if we're just missing green cards !!!
        # play a land if possible
        if lands_in_hand and land_drop_left:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)

            process_played_land(
                land,
                hand,
                battlefield,
                mana_pool,
                mana_pool_for_turn,
                lands_in_hand,
                deck,
                missing_sac_target,
                missing_sac_outlet,
                missing_green_cards,
                missing_mana_to_cast_sac_outlet,
                missing_cantrip,
            )

        win, (missing_mana_to_cast_sac_outlet, missing_sac_target, missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
        if win:
            return turn, starting_hand
    return None

def rollout_from_state(hand, deck, battlefield, mana_pool, turn, turns_to_win=10):
    """
    Run a single game to completion from a given mid-game state.
    Returns the win turn, or None if no win within turns_to_win.
 
    All inputs are deep-copied internally so the caller's state is never mutated.
    """
 
    hand        = copy.deepcopy(hand)
    deck        = copy.deepcopy(deck)
    battlefield = copy.deepcopy(battlefield)
    mana_pool   = copy.deepcopy(mana_pool)
 
    # ── resume from the current turn (don't re-draw for the turn already in progress) ──
    for t in range(turn, turns_to_win + 1):
        # draw only for turns *after* the one we branched from
        if t != turn:
            drawn = draw(deck, 1)
            if drawn:
                hand.extend(drawn)
 
        mana_pool_for_turn = mana_pool.copy()
        land_drop_left = True
 
        lands_in_hand = [card for card in hand if card[1].land]
 
        win, (missing_mana_to_cast_sac_outlet, missing_sac_target, missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
        castable_cantrips, missing_cantrip, missing_mana_to_cast_cantrip = check_for_cantrip(hand, mana_pool_for_turn)
 
        if win:
            return t
 
        missing_mana_count = [len(m) for m in missing_mana_to_cast_sac_outlet]
 
        if len(missing_mana_count) > 0 and (np.min(missing_mana_count) == 1) and lands_in_hand:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)
            process_played_land(land, hand, battlefield, mana_pool, mana_pool_for_turn, lands_in_hand, deck, missing_sac_target, missing_sac_outlet, missing_green_cards, missing_mana_to_cast_sac_outlet, missing_cantrip)
 
            win, (missing_mana_to_cast_sac_outlet, missing_sac_target, missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
            if win:
                return t
 
        if len(castable_cantrips) > 0:
            mana_pool_for_turn = cantrip(castable_cantrips[0], mana_pool_for_turn, hand, deck, missing_sac_target, missing_sac_outlet, missing_mana_to_cast_sac_outlet, lands_in_hand, missing_green_cards)
 
        missing_mana_count = [len(m) for m in missing_mana_to_cast_cantrip]
 
        if len(missing_mana_count) > 0 and (np.min(missing_mana_count) == 1) and lands_in_hand and land_drop_left:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)
            process_played_land(land, hand, battlefield, mana_pool, mana_pool_for_turn, lands_in_hand, deck, missing_sac_target, missing_sac_outlet, missing_green_cards, missing_mana_to_cast_cantrip, missing_cantrip)
            castable_cantrips, missing_cantrip, missing_mana_to_cast_cantrip = check_for_cantrip(hand, mana_pool_for_turn)
            if len(castable_cantrips) > 0:
                mana_pool_for_turn = cantrip(castable_cantrips[0], mana_pool_for_turn, hand, deck, missing_sac_target, missing_sac_outlet, missing_mana_to_cast_sac_outlet, lands_in_hand, missing_green_cards)
 
        if lands_in_hand and land_drop_left:
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)
            process_played_land(land, hand, battlefield, mana_pool, mana_pool_for_turn, lands_in_hand, deck, missing_sac_target, missing_sac_outlet, missing_green_cards, missing_mana_to_cast_sac_outlet, missing_cantrip)
 
        win, _ = check_for_win(hand, mana_pool_for_turn, deck)
        if win:
            return t
 
    return None

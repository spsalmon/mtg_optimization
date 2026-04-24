"""
collect_surveil_data.py

Runs many games and, at every surveil decision point, branches into one 'keep'
game and one 'bin' game. Variance averages out across tens of thousands of games.

Usage:
    from neoform.data_collection.collect_surveil_data import collect_surveil_dataset
    rows = collect_surveil_dataset(deck_list, n_games=50000)
"""

import copy
import numpy as np
from tqdm import tqdm

from neoform.utils import initialize_deck, parse_decklist
from neoform.engine.game_actions import (
    draw,
    play_land,
    cantrip,
    check_for_win,
    check_for_cantrip,
    process_played_land,
)
from neoform.engine.features import extract_surveil_game_state
from neoform.simulate import rollout_from_state
import polars as pl

# ---------------------------------------------------------------------------
# Internal: one game that yields dataset rows at every surveil decision point
# ---------------------------------------------------------------------------

def _simulate_game_collecting_surveil(deck_list, on_the_play, turns_to_win=10):
    """
    Play one game with the hand-coded policy.
    Every time a surveil decision would be made, branch and collect a dataset row.

    Returns a list of row dicts (one per surveil decision encountered).
    """
    rows = []

    deck        = initialize_deck(deck_list)
    hand        = draw(deck, 7)
    battlefield = []
    mana_pool   = []

    for turn in range(1, turns_to_win + 1):
        if turn != 1 or not on_the_play:
            drawn = draw(deck, 1)
            if drawn:
                hand.extend(drawn)

        mana_pool_for_turn = mana_pool.copy()
        land_drop_left = True

        lands_in_hand = [card for card in hand if card[1].land]

        win, (missing_mana_to_cast_sac_outlet, missing_sac_target,
              missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
        castable_cantrips, missing_cantrip, missing_mana_to_cast_cantrip = check_for_cantrip(hand, mana_pool_for_turn)

        if win:
            break

        missing_mana_count = [len(m) for m in missing_mana_to_cast_sac_outlet]

        if len(missing_mana_count) > 0 and (np.min(missing_mana_count) == 1) and lands_in_hand:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)

            # ── intercept surveil before it fires inside process_played_land ──
            rows += _maybe_collect_surveil_row(
                land, hand, deck, battlefield, mana_pool, mana_pool_for_turn,
                lands_in_hand, missing_sac_target, missing_sac_outlet,
                missing_green_cards, missing_mana_to_cast_sac_outlet,
                missing_cantrip, turn, on_the_play,
            )

            process_played_land(land, hand, battlefield, mana_pool, mana_pool_for_turn,
                                lands_in_hand, deck, missing_sac_target, missing_sac_outlet,
                                missing_green_cards, missing_mana_to_cast_sac_outlet, missing_cantrip)

            win, (missing_mana_to_cast_sac_outlet, missing_sac_target,
                  missing_sac_outlet, missing_green_cards) = check_for_win(hand, mana_pool_for_turn, deck)
            if win:
                break

        if len(castable_cantrips) > 0:
            mana_pool_for_turn = cantrip(
                castable_cantrips[0], mana_pool_for_turn, hand, deck,
                missing_sac_target, missing_sac_outlet,
                missing_mana_to_cast_sac_outlet, lands_in_hand, missing_green_cards,
            )

        missing_mana_count = [len(m) for m in missing_mana_to_cast_cantrip]

        if len(missing_mana_count) > 0 and (np.min(missing_mana_count) == 1) and lands_in_hand and land_drop_left:
            land_drop_left = False
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)

            rows += _maybe_collect_surveil_row(
                land, hand, deck, battlefield, mana_pool, mana_pool_for_turn,
                lands_in_hand, missing_sac_target, missing_sac_outlet,
                missing_green_cards, missing_mana_to_cast_cantrip,
                missing_cantrip, turn, on_the_play,
            )

            process_played_land(land, hand, battlefield, mana_pool, mana_pool_for_turn,
                                lands_in_hand, deck, missing_sac_target, missing_sac_outlet,
                                missing_green_cards, missing_mana_to_cast_cantrip, missing_cantrip)

            castable_cantrips, missing_cantrip, missing_mana_to_cast_cantrip = check_for_cantrip(hand, mana_pool_for_turn)
            if len(castable_cantrips) > 0:
                mana_pool_for_turn = cantrip(
                    castable_cantrips[0], mana_pool_for_turn, hand, deck,
                    missing_sac_target, missing_sac_outlet,
                    missing_mana_to_cast_sac_outlet, lands_in_hand, missing_green_cards,
                )

        if lands_in_hand and land_drop_left:
            land = play_land(lands_in_hand, missing_mana_to_cast_sac_outlet)

            rows += _maybe_collect_surveil_row(
                land, hand, deck, battlefield, mana_pool, mana_pool_for_turn,
                lands_in_hand, missing_sac_target, missing_sac_outlet,
                missing_green_cards, missing_mana_to_cast_sac_outlet,
                missing_cantrip, turn, on_the_play,
            )

            process_played_land(land, hand, battlefield, mana_pool, mana_pool_for_turn,
                                lands_in_hand, deck, missing_sac_target, missing_sac_outlet,
                                missing_green_cards, missing_mana_to_cast_sac_outlet, missing_cantrip)

        win, _ = check_for_win(hand, mana_pool_for_turn, deck)
        if win:
            break

    return rows


# ---------------------------------------------------------------------------
# Helper: collect one surveil data row if this land triggers a surveil
# ---------------------------------------------------------------------------

def _maybe_collect_surveil_row(
    land, hand, deck, battlefield, mana_pool, mana_pool_for_turn,
    lands_in_hand, missing_sac_target, missing_sac_outlet, missing_green_cards,
    missing_mana, missing_cantrip, turn, on_the_play,
):
    """
    If `land` has a surveil trigger AND the deck is non-empty, branch into
    one 'keep' game and one 'bin' game and return a dataset row.
    Otherwise return [].
    """
    if not (land is not None and getattr(land[1], "surveil", False) and len(deck) > 0):
        return []

    # Snapshot state after the land resolves but before surveil fires
    hand_after   = copy.deepcopy(hand)
    deck_snap    = copy.deepcopy(deck)
    bf_after     = copy.deepcopy(battlefield)
    mana_after   = copy.deepcopy(mana_pool)
    mana_t_after = copy.deepcopy(mana_pool_for_turn)

    if land in hand_after:
        hand_after.remove(land)
    bf_after.append(land)
    land_production = []
    if getattr(land[1], "produces_green", False):
        land_production.append('G')
    if getattr(land[1], "produces_blue", False):
        land_production.append('U')
    if getattr(land[1], "untapped", False):
        mana_t_after.append(land_production)
    mana_after.append(land_production)

    features = extract_surveil_game_state(
        deck_snap, hand_after, mana_t_after,
        missing_sac_target, missing_sac_outlet, missing_mana,
        [c for c in hand_after if c[1].land],
        missing_green_cards, missing_cantrip, turn,
    )

    # One game per branch — variance averages out across tens of thousands of games
    keep_deck = copy.deepcopy(deck_snap)
    bin_deck  = copy.deepcopy(deck_snap)
    bin_deck.pop(0)

    NO_WIN = 11
    keep_result = rollout_from_state(hand_after, keep_deck, bf_after, mana_after, turn, on_the_play)
    bin_result  = rollout_from_state(hand_after, bin_deck,  bf_after, mana_after, turn, on_the_play)

    keep_turn = keep_result if keep_result is not None else NO_WIN
    bin_turn  = bin_result  if bin_result  is not None else NO_WIN

    row = {
        **features,
        "keep_win_turn":  keep_turn,
        "bin_win_turn":   bin_turn,
        "keep_is_better": int(keep_turn <= bin_turn),
        "value_of_keeping": bin_turn - keep_turn,  # >0 means keep is better
    }
    return [row]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def collect_surveil_dataset(deck_list, n_games=500, on_the_play=False):
    """
    Run `n_games` games, branching at every surveil decision to collect training data.
    Each branch runs one game — variance averages out across many games.

    Returns list[dict] — one dict per surveil decision encountered.
    """
    all_rows = []
    for _ in tqdm(range(n_games), desc="Collecting surveil data"):
        rows = _simulate_game_collecting_surveil(deck_list, on_the_play)
        all_rows.extend(rows)
    return all_rows

deck_list_str = """
4 Allosaurus Rider
1 Atraxa, Grand Unifier
1 Boseiju, Who Endures
1 Breeding Pool
1 Bridgeworks Battle
4 Consign to Memory
2 Disciple of Freyalise
4 Eldritch Evolution
1 Endurance
1 Flooded Strand
1 Generous Ent
2 Ghalta, Stampede Tyrant
1 Griselbrand
3 Hedge Maze
1 Hooting Mandrills
4 Misty Rainforest
4 Neoform
2 Nourishing Shoal
4 Pact of Negation
4 Planar Genesis
1 Scalding Tarn
2 Snow-Covered Forest
1 Snow-Covered Island
4 Summoner's Pact
1 Ureni, the Song Unending
3 Veil of Summer
1 Wooded Foothills
1 Xenagos, God of Revels
"""

deck_list = parse_decklist(deck_list_str)
rows = collect_surveil_dataset(deck_list, n_games=100, on_the_play=False)
dataframe = pl.DataFrame(rows)
print(dataframe)
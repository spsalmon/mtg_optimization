import numpy as np

def extract_surveil_game_state(deck, hand, mana_pool_for_turn, missing_sac_target, missing_sac_outlet, missing_mana, lands_in_hand, missing_green_cards, missing_cantrip, turn):
    """
    Extract a feature dict representing the state at a surveil decision point.
    This is the input to the future learned model.
    """
    card_on_top = deck[0]
    tags = card_on_top[1]
 
    if len(missing_mana) > 0:
        missing_mana_count = int(np.min([len(m) for m in missing_mana]))
    else:
        missing_mana_count = 0
 
    hand_sac_outlets = sum(1 for c in hand if c[1].sac_outlet)
    hand_sac_targets = sum(1 for c in hand if c[1].sac_target)
    hand_lands       = sum(1 for c in hand if c[1].land)
    hand_green_cards = sum(1 for c in hand if c[1].green)
    hand_cantrips    = sum(1 for c in hand if c[1].cantrip)
 
    mana_green = sum(1 for src in mana_pool_for_turn if 'G' in src)
    mana_blue  = sum(1 for src in mana_pool_for_turn if 'U' in src)
 
    return {
        # card on top of deck
        "card_name":          card_on_top[0],
        "card_is_sac_outlet": bool(tags.sac_outlet),
        "card_is_sac_target": bool(tags.sac_target),
        "card_is_land":       bool(tags.land),
        "card_is_green":      bool(tags.green),
        "card_is_cantrip":    bool(tags.cantrip),
        "card_cantrip_power": int(tags.cantrip_power) if tags.cantrip_power else 0,
 
        # hand composition
        "hand_size":          len(hand),
        "hand_sac_outlets":   hand_sac_outlets,
        "hand_sac_targets":   hand_sac_targets,
        "hand_lands":         hand_lands,
        "hand_green_cards":   hand_green_cards,
        "hand_cantrips":      hand_cantrips,
 
        # mana available this turn
        "mana_green":         mana_green,
        "mana_blue":          mana_blue,
 
        # missing flags
        "missing_sac_outlet": bool(missing_sac_outlet),
        "missing_sac_target": bool(missing_sac_target),
        "missing_green_cards":bool(missing_green_cards),
        "missing_cantrip":    bool(missing_cantrip),
        "missing_mana_count": missing_mana_count,
 
        # game context
        "turn": turn,
    }

def get_missing_mana(card, mana_pool = []):
    temp_mana_pool = mana_pool.copy()
    cost = card[1].cost
    missing_mana = []
    for pip in cost:
        if pip != "C":
            # for colored mana, check if we have a land that only produces that mana and tap it, if not, tap a dual
            candidates = [i for i, src in enumerate(temp_mana_pool) if src == [pip]]
            if len(candidates) > 0:
                temp_mana_pool.pop(candidates[0])
            else:
                candidates = [i for i, src in enumerate(temp_mana_pool) if pip in src]
                if len(candidates) > 0:
                    temp_mana_pool.pop(candidates[0])
                else:
                    missing_mana.append(pip)
        else:
            # for generic mana, tap the land of the color we have the most of, if equal, tap green (?)
            candidates = [i for i, src in enumerate(temp_mana_pool) if len(src) == 1]
            
            if len(candidates) > 0:
                green_singles = sum(1 for i in candidates if temp_mana_pool[i] == ['G'])
                blue_singles  = sum(1 for i in candidates if temp_mana_pool[i] == ['U'])
                if green_singles >= blue_singles:
                    candidates = [i for i, src in enumerate(temp_mana_pool) if src == ['G']]
                    temp_mana_pool.pop(candidates[0])
                else:
                    candidates = [i for i, src in enumerate(temp_mana_pool) if src == ['U']]
                    temp_mana_pool.pop(candidates[0])
            else:
                candidates = [i for i, src in enumerate(temp_mana_pool) if len(src) > 0]
                if len(candidates) > 0:
                    temp_mana_pool.pop(candidates[0])
                else:
                    missing_mana.append(pip)

    return missing_mana

def pay_mana_cost(cost, mana_pool):
    temp_mana_pool = mana_pool.copy()
    for pip in cost:
        if pip != "C":
            candidates = [i for i, src in enumerate(temp_mana_pool) if src == [pip]]
            if len(candidates) > 0:
                temp_mana_pool.pop(candidates[0])
            else:
                candidates = [i for i, src in enumerate(temp_mana_pool) if pip in src]
                if len(candidates) > 0:
                    temp_mana_pool.pop(candidates[0])
        else:
            # for generic mana, tap the land of the color we have the most of, if equal, tap green (?)
            candidates = [i for i, src in enumerate(temp_mana_pool) if len(src) == 1]
            if len(candidates) > 0:
                green_singles = sum(1 for i in candidates if temp_mana_pool[i] == ['G'])
                blue_singles  = sum(1 for i in candidates if temp_mana_pool[i] == ['U'])

                if green_singles >= blue_singles:
                    candidates = [i for i, src in enumerate(temp_mana_pool) if src == ['G']]
                    temp_mana_pool.pop(candidates[0])
                else:
                    candidates = [i for i, src in enumerate(temp_mana_pool) if src == ['U']]
                    temp_mana_pool.pop(candidates[0])
            else:
                candidates = [i for i, src in enumerate(temp_mana_pool) if len(src) > 0] # we cannot tap fetch lands for mana
                if len(candidates) > 0:
                    temp_mana_pool.pop(candidates[0])
    return temp_mana_pool

def get_mana_production_of_land(land):
    tags = land[1]
    if tags.land_type:
        return len(tags.land_type)
    else:
        return 1 
    
def check_if_castable(card, mana_pool=[]):
    missing_mana = get_missing_mana(card, mana_pool)
    return len(missing_mana) == 0
class card_tag:
    def __init__(self, cost = None, land = False, fetch = False, cycle = False, cycle_cost = None, surveil = False, fetch_cost = None, land_type = None, can_fetch = None, protection = False, untapped = True, sac_target = False, sac_outlet = False, produces_green = False, produces_blue = False, green = False, pitch_cost = None, cantrip = False, cantrip_power = None,):
        self.cost = cost
        self.land = land
        self.fetch = fetch
        self.surveil = surveil
        self.fetch_cost = fetch_cost
        self.land_type = land_type
        self.can_fetch = can_fetch
        self.untapped = untapped
        self.protection = protection
        self.sac_target = sac_target
        self.sac_outlet = sac_outlet
        self.produces_green = produces_green
        self.produces_blue = produces_blue
        self.green = green
        self.pitch_cost = pitch_cost
        self.cycle = cycle
        self.cycle_cost = cycle_cost
        self.cantrip = cantrip
        self.cantrip_power = cantrip_power

CARD_TAGS = {
    # fetches
    "Flooded Strand": card_tag(land=True, fetch=True, can_fetch=['Island', 'Plain']),
    "Misty Rainforest": card_tag(land=True, fetch=True, can_fetch=['Island', 'Forest']),
    "Scalding Tarn": card_tag(land=True, fetch=True, can_fetch=['Island', 'Mountain']),
    "Wooded Foothills": card_tag(land=True, fetch=True, can_fetch=['Mountain', 'Forest']),

    # other lands
    "Breeding Pool" : card_tag(land=True, produces_green=True, produces_blue=True, land_type=["Forest", "Island"]),
    "Boseiju, Who Endures" : card_tag(land=True, produces_green=True),
    "Forest": card_tag(land=True, land_type=["Forest"], produces_green=True),
    "Snow-Covered Forest": card_tag(land=True, land_type=["Forest"], produces_green=True),
    "Island" : card_tag(land=True, land_type=['Island'], produces_green=False, produces_blue=True),
    "Snow-Covered Island" : card_tag(land=True, land_type=['Island'], produces_green=False, produces_blue=True),
    "Hedge Maze": card_tag(land=True, untapped=False, produces_green=True, produces_blue=True, land_type=['Island', "Forest"], surveil=True,),

    # MDFC
    "Bridgeworks Battle" : card_tag(land=True, green=True, produces_green=True),
    "Disciple of Freyalise" : card_tag(land=True, green=True, produces_green=True),

    # sac outlets
    "Neoform": card_tag(cost = "UG", sac_outlet=True, green=True,),
    "Eldritch Evolution": card_tag(cost = "GGC", sac_outlet=True, green=True,),

    # protection
    "Veil of Summer": card_tag(cost = "G", green=True, protection=True),
    "Pact of Negation" : card_tag(protection=True),

    # cantrips
    "Planar Genesis": card_tag(cost = "UG", green=True, cantrip=True, cantrip_power=4),
    "Preordain": card_tag(cost = "U", cantrip=True, cantrip_power=3),

    # other cards
    "Allosaurus Rider" : card_tag(sac_target=True, green=True, pitch_cost="GG"),
    "Atraxa, Grand Unifier" : card_tag(green=True),
    "Consign to Memory" : card_tag(),
    "Endurance": card_tag(green=True),
    "Generous Ent": card_tag(green=True, cycle=True, can_fetch=["Forest"], cycle_cost=1),
    "Ghalta, Stampede Tyrant": card_tag(green=True,),
    "Griselbrand": card_tag(),
    "Hooting Mandrills": card_tag(green=True), # for now I'll ignore mandrills, I'll implement delve later
    
    "Summoner's Pact": card_tag(sac_target=True, green=True, pitch_cost="GG"), # for now we'll just consider pact as additional copies of Rider
    "Xenagos, God of Revels": card_tag(green=True),
    "Nourishing Shoal": card_tag(green=True),
    "Ureni, the Song Unending": card_tag(green=True),
}
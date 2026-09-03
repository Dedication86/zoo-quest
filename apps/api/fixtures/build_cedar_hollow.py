"""
Builds the Cedar Hollow Zoo prototype fixture (Django fixture format) and
validates every cross-reference. Output: cedar_hollow_seed.json

App labels assumed by the schema doc:
  tenants  -> Zoo, StaffMembership
  content  -> Exhibit, Animal, Marker, Challenge, Quest, QuestChallenge, Badge, Level
"""

import json

fx = []
ids = {}  # (model, slug) -> pk


def add(model, pk, **fields):
    fx.append({"model": model, "pk": pk, "fields": fields})
    return pk


ZOO = add(
    "tenants.zoo",
    1,
    name="Cedar Hollow Zoo",
    slug="cedar-hollow",
    timezone="America/Chicago",
    primary_color="#2F6B4F",
    is_active=True,
    settings={
        "discovery_xp": 100,
        "quest_complete_xp": 500,
        "xp_by_difficulty": {"easy": 50, "medium": 100, "hard": 250},
        "repeat_scan_cooldown_minutes": 1440,
    },
)

# ---------- Levels ----------
for n, (title, xp) in enumerate(
    [
        ("Zoo Rookie", 0),
        ("Animal Explorer", 300),
        ("Wildlife Detective", 800),
        ("Conservation Ranger", 1500),
        ("Zoo Master", 2500),
    ],
    start=1,
):
    add("content.level", n, zoo=ZOO, number=n, title=title, xp_required=xp)

# ---------- Exhibits (map_x / map_y are % of the static map image) ----------
exhibits = [
    (
        "base-camp",
        "Base Camp",
        "Zoo entrance plaza and Conservation Station. Every adventure starts here.",
        50,
        92,
    ),
    (
        "african-savanna",
        "African Savanna",
        "Open grasslands where giraffes, zebras and elephants roam in view of the lion ridge.",
        22,
        30,
    ),
    (
        "rainforest-trail",
        "Rainforest Trail",
        "A shaded canopy walk full of monkeys, macaws and one very slow sloth.",
        72,
        28,
    ),
    ("reptile-house", "Reptile House", "Cool, dim and quiet. Home to the zoo's oldest resident.", 78, 62),
    (
        "wild-north",
        "Wild North",
        "Pine woodland habitat for red wolves and other North American natives.",
        24,
        66,
    ),
]
for i, (slug, name, desc, x, y) in enumerate(exhibits, start=1):
    ids[("exhibit", slug)] = add(
        "content.exhibit",
        i,
        zoo=ZOO,
        slug=slug,
        name=name,
        description=desc,
        map_x=x,
        map_y=y,
        sort_order=i,
        is_active=True,
    )

# ---------- Animals ----------
animals = [
    # slug, name, species, sci name, exhibit, emoji, IUCN, tags, facts, conservation note
    (
        "giraffe",
        "Giraffe",
        "Reticulated giraffe",
        "Giraffa reticulata",
        "african-savanna",
        "🦒",
        "EN",
        ["africa", "mammal", "herbivore", "tall", "spots"],
        [
            "A giraffe's tongue is about 18 inches long and dark purple to protect it from sunburn.",
            "Giraffes only need 5 to 30 minutes of sleep a day.",
            "Every giraffe has a unique spot pattern, like a fingerprint.",
        ],
        "Giraffe numbers have dropped about 40% in 30 years, mostly from habitat loss and poaching.",
    ),
    (
        "elephant",
        "African Elephant",
        "African savanna elephant",
        "Loxodonta africana",
        "african-savanna",
        "🐘",
        "EN",
        ["africa", "mammal", "herbivore", "big-ears", "trunk", "heavy"],
        [
            "An elephant's trunk has about 40,000 muscles. Your whole body has around 600.",
            "Elephants can recognize themselves in a mirror.",
            "They dig water holes in dry riverbeds that other animals rely on.",
        ],
        "Elephants are 'ecosystem engineers': they spread seeds, open paths through brush and create water sources for dozens of other species.",
    ),
    (
        "zebra",
        "Plains Zebra",
        "Plains zebra",
        "Equus quagga",
        "african-savanna",
        "🦓",
        "NT",
        ["africa", "mammal", "herbivore", "stripes"],
        [
            "No two zebras have the same stripe pattern.",
            "Stripes may confuse biting flies and help zebras keep cool.",
            "Zebras sleep standing up.",
        ],
        "Plains zebras are still widespread but fenced migration routes are shrinking their range.",
    ),
    (
        "lion",
        "African Lion",
        "African lion",
        "Panthera leo",
        "african-savanna",
        "🦁",
        "VU",
        ["africa", "mammal", "carnivore", "big-cat", "mane"],
        [
            "A lion's roar can be heard from 5 miles away.",
            "Lions rest up to 20 hours a day.",
            "Lionesses do most of the hunting, usually as a team.",
        ],
        "Wild lions have lost about 90% of their historic range. Fewer than 25,000 remain in Africa.",
    ),
    (
        "squirrel-monkey",
        "Squirrel Monkey",
        "Common squirrel monkey",
        "Saimiri sciureus",
        "rainforest-trail",
        "🐒",
        "LC",
        ["south-america", "mammal", "primate", "rainforest", "tail"],
        [
            "Squirrel monkeys live in troops of up to 300.",
            "They use their tails for balance, not for hanging.",
            "Their brain is huge for their body size.",
        ],
        "Rainforest clearing for farming is the biggest threat to squirrel monkey habitat.",
    ),
    (
        "scarlet-macaw",
        "Scarlet Macaw",
        "Scarlet macaw",
        "Ara macao",
        "rainforest-trail",
        "🦜",
        "LC",
        ["south-america", "bird", "rainforest", "colorful", "red"],
        [
            "Scarlet macaws can live 50 years or more.",
            "They mate for life and are often seen flying in pairs.",
            "Their beak is strong enough to crack a Brazil nut.",
        ],
        "Macaws are heavily targeted by the illegal pet trade. Never buy a wild-caught parrot.",
    ),
    (
        "sloth",
        "Two-toed Sloth",
        "Linnaeus's two-toed sloth",
        "Choloepus didactylus",
        "rainforest-trail",
        "🦥",
        "LC",
        ["south-america", "mammal", "rainforest", "slow", "upside-down", "nocturnal"],
        [
            "Sloths move so slowly that algae grows on their fur, turning them green.",
            "A sloth only climbs down from its tree about once a week.",
            "They can turn their heads almost all the way around.",
        ],
        "Sloths need connected forest canopy. Roads and power lines are a major danger to them.",
    ),
    (
        "burmese-python",
        "Burmese Python",
        "Burmese python",
        "Python bivittatus",
        "reptile-house",
        "🐍",
        "VU",
        ["asia", "reptile", "snake", "long", "no-legs"],
        [
            "Burmese pythons can grow longer than a pickup truck.",
            "They swallow prey whole and can go months between meals.",
            "They sense heat with special pits along their lips.",
        ],
        "In Asia, Burmese pythons are threatened by hunting for skins. In Florida they are an invasive species released by pet owners.",
    ),
    (
        "tortoise",
        "Galápagos Tortoise",
        "Galápagos giant tortoise",
        "Chelonoidis niger",
        "reptile-house",
        "🐢",
        "VU",
        ["islands", "reptile", "shell", "old", "slow"],
        [
            "Galápagos tortoises can live more than 100 years.",
            "They can weigh over 500 pounds.",
            "They can survive a year without food or water.",
        ],
        "Whalers once took thousands of tortoises for food. Breeding programs have brought some island populations back from just a dozen animals.",
    ),
    (
        "red-wolf",
        "Red Wolf",
        "Red wolf",
        "Canis rufus",
        "wild-north",
        "🐺",
        "CR",
        ["north-america", "mammal", "carnivore", "pack", "endangered"],
        [
            "Red wolves are found only in the United States.",
            "They live in small family packs and hunt mostly at night.",
            "Pups are born in the spring, usually four to six at a time.",
        ],
        "The red wolf is one of the most endangered animals on Earth. Only a few dozen live in the wild, all in North Carolina. Zoo breeding programs are keeping the species alive.",
    ),
]
for i, (slug, name, species, sci, ex, emoji, iucn, tags, facts, cons) in enumerate(animals, start=1):
    ids[("animal", slug)] = add(
        "content.animal",
        i,
        zoo=ZOO,
        slug=slug,
        name=name,
        species=species,
        scientific_name=sci,
        exhibit=ids[("exhibit", ex)],
        emoji=emoji,
        conservation_status=iucn,
        tags=tags,
        fun_facts=facts,
        description=f"{name} at {dict((e[0], e[1]) for e in exhibits)[ex]}.",
        conservation_info=cons,
        is_active=True,
    )

# ---------- Markers (QR codes). Code is what gets printed: /s/<code> ----------
markers = [("CHZ-BASECAMP-001", "base-camp", None, "Base Camp welcome sign")]
for slug, name, *_rest in animals:
    ex = _rest[2]
    markers.append((f"CHZ-{slug.upper().replace('-', '')}-001", ex, slug, f"{name} viewing rail"))
for i, (code, ex, an, label) in enumerate(markers, start=1):
    ids[("marker", an or "base-camp")] = add(
        "content.marker",
        i,
        zoo=ZOO,
        code=code,
        exhibit=ids[("exhibit", ex)],
        animal=ids[("animal", an)] if an else None,
        label=label,
        is_active=True,
    )

# ---------- Challenges ----------
XP = {"easy": 50, "medium": 100, "hard": 250}
challenges = []


def ch(
    slug,
    ctype,
    difficulty,
    title,
    prompt,
    hint=None,
    animal=None,
    exhibit=None,
    accept_markers=None,
    config=None,
    explanation="",
    xp=None,
):
    challenges.append(
        dict(
            slug=slug,
            type=ctype,
            difficulty=difficulty,
            title=title,
            prompt=prompt,
            hint=hint,
            animal=animal,
            exhibit=exhibit,
            accept_markers=accept_markers or [],
            config=config or {},
            explanation=explanation,
            xp=xp or XP[difficulty],
        )
    )


# Animal hunts (scan the specific animal's marker)
ch(
    "find-giraffe",
    "animal_hunt",
    "easy",
    "Find a Giraffe",
    "Head to the African Savanna and find the tallest animal in the zoo. Scan the quest marker at its viewing rail.",
    hint="Look up. Way up.",
    animal="giraffe",
    accept_markers=["giraffe"],
    explanation="Giraffes are the tallest land animals on Earth. Adults can reach 18 feet.",
)
ch(
    "find-elephant",
    "animal_hunt",
    "easy",
    "Find an Elephant",
    "Find the heaviest animal in the Savanna and scan its marker.",
    hint="Follow the sound of splashing water.",
    animal="elephant",
    accept_markers=["elephant"],
    explanation="An adult African elephant can weigh as much as four cars.",
)
ch(
    "find-lion",
    "animal_hunt",
    "medium",
    "Find the Lion",
    "The king of the Savanna is watching from the ridge. Find the lion and scan the marker.",
    hint="Look for the rocky high ground at the far end of the Savanna.",
    animal="lion",
    accept_markers=["lion"],
    explanation="Lions are the only cats that live in family groups, called prides.",
)
ch(
    "find-monkey",
    "animal_hunt",
    "easy",
    "Find a Monkey",
    "Somewhere on the Rainforest Trail a troop of monkeys is causing trouble. Find them and scan the marker.",
    hint="Listen for chattering in the treetops.",
    animal="squirrel-monkey",
    accept_markers=["squirrel-monkey"],
    explanation="Squirrel monkeys are some of the smallest monkeys in the Americas, about the size of a squirrel.",
)

# Scavenger hunts (clue-based; may accept more than one marker)
ch(
    "stripes",
    "scavenger",
    "easy",
    "Something With Stripes",
    "Find an animal with black and white stripes and scan its marker.",
    hint="It's a relative of the horse.",
    accept_markers=["zebra"],
    explanation="Scientists think zebra stripes confuse biting flies, which struggle to land on striped surfaces.",
)
ch(
    "upside-down",
    "scavenger",
    "medium",
    "Hanging Around",
    "Find an animal that spends most of its life hanging upside down. Scan its marker.",
    hint="It's on the Rainforest Trail, and it is in no hurry.",
    accept_markers=["sloth"],
    explanation="Sloths hang upside down so much that their fur grows away from their belly, so rain runs off.",
)
ch(
    "hundred-years",
    "scavenger",
    "medium",
    "Older Than Your Grandparents",
    "Find an animal that can live more than 100 years. Scan its marker.",
    hint="Slow and steady. Check the Reptile House.",
    accept_markers=["tortoise"],
    explanation="Some Galápagos tortoises alive today were born before cars were invented.",
)
ch(
    "colorful-bird",
    "scavenger",
    "easy",
    "Find a Colorful Bird",
    "Find the brightest bird on the Rainforest Trail and scan its marker.",
    hint="Red, yellow and blue. Loud, too.",
    accept_markers=["scarlet-macaw"],
    explanation="Bright colors help macaws find each other in the dense green canopy.",
)
ch(
    "find-reptile",
    "scavenger",
    "easy",
    "Find a Reptile",
    "Find any reptile in the zoo and scan its marker.",
    hint="The Reptile House is a good bet.",
    accept_markers=["burmese-python", "tortoise"],
    explanation="Reptiles are cold-blooded, so they use the sun or warm rocks to control their body temperature.",
)

# Who Am I? (multiple choice, riddle)
ch(
    "who-elephant",
    "who_am_i",
    "easy",
    "Who Am I?",
    "I weigh more than a car. I have huge ears. I use my nose like a hand. Who am I?",
    animal="elephant",
    config={"options": ["Elephant", "Rhino", "Hippo", "Giraffe"], "correct": "Elephant"},
    explanation="Elephants use their trunks to drink, grab food, greet friends and even snorkel.",
)
ch(
    "who-giraffe",
    "who_am_i",
    "medium",
    "Who Am I?",
    "My tongue is purple and longer than a ruler. I have a very long neck but the same number of neck bones as you. Who am I?",
    animal="giraffe",
    config={"options": ["Ostrich", "Giraffe", "Zebra", "Camel"], "correct": "Giraffe"},
    explanation="Giraffes and humans both have seven neck bones. Each giraffe neck bone is about 10 inches long.",
)
ch(
    "who-python",
    "who_am_i",
    "hard",
    "Who Am I?",
    "I have no legs but I can climb trees. I can go months without eating. I sense heat with my lips. Who am I?",
    animal="burmese-python",
    config={"options": ["Crocodile", "Tortoise", "Python", "Lizard"], "correct": "Python"},
    explanation="Pythons have heat-sensing pits on their lips that let them 'see' warm-blooded prey in the dark.",
)

# Observation (any answer counts: the goal is to make the family actually watch)
ch(
    "watch-giraffes",
    "observation",
    "easy",
    "Watch the Giraffes",
    "Stand at the giraffe rail and watch for 30 seconds. What are they doing?",
    animal="giraffe",
    exhibit="african-savanna",
    config={
        "timer_seconds": 30,
        "options": ["Eating", "Walking", "Resting", "Drinking", "Something else"],
        "any_answer_correct": True,
    },
    explanation="Giraffes eat up to 75 pounds of leaves a day, so 'eating' is the most common answer here.",
)
ch(
    "count-monkeys",
    "observation",
    "easy",
    "Monkey Count",
    "Watch the squirrel monkeys for 30 seconds. How many can you count?",
    animal="squirrel-monkey",
    exhibit="rainforest-trail",
    config={
        "timer_seconds": 30,
        "options": ["1 to 3", "4 to 6", "7 or more", "They're hiding!"],
        "any_answer_correct": True,
    },
    explanation="Squirrel monkeys are hard to count because they never stop moving. Zookeepers count them at feeding time.",
)
ch(
    "sloth-watch",
    "observation",
    "medium",
    "Sloth Watch",
    "Find the sloth and watch it for 30 seconds. Did it move?",
    animal="sloth",
    exhibit="rainforest-trail",
    config={
        "timer_seconds": 30,
        "options": ["Yes, a little", "Yes, a lot", "Not at all", "I can't find it"],
        "any_answer_correct": True,
    },
    explanation="Sloths sleep 15 to 20 hours a day. Not moving is a completely normal sloth answer.",
)

# Photo (honor system in MVP; no upload)
ch(
    "photo-eating",
    "photo",
    "easy",
    "Photo Safari: Snack Time",
    "Take a photo of any animal eating. Show your team, then tap Done.",
    config={"verification": "self_report"},
    explanation="Zoo nutritionists plan every animal's meals. Elephants alone eat about 300 pounds of food a day.",
)
ch(
    "photo-team-sign",
    "photo",
    "easy",
    "Photo Safari: Team Photo",
    "Take a team photo in front of the Base Camp sign to start your adventure.",
    exhibit="base-camp",
    config={"verification": "self_report"},
    explanation="Explorers always document the start of an expedition.",
)

# Conservation (quiz with a real takeaway)
ch(
    "cons-elephant",
    "conservation",
    "medium",
    "Ecosystem Engineers",
    "Why are elephants so important to the animals around them?",
    animal="elephant",
    config={
        "options": [
            "They scare away predators",
            "They dig water holes and spread seeds",
            "They keep the grass short",
            "They are the biggest",
        ],
        "correct": "They dig water holes and spread seeds",
    },
    explanation="Elephants dig for water in dry riverbeds and other animals drink there. Seeds pass through them and grow into new trees miles away.",
)
ch(
    "cons-red-wolf",
    "conservation",
    "hard",
    "The Rarest Wolf",
    "About how many red wolves are left in the wild?",
    animal="red-wolf",
    config={
        "options": ["Fewer than 50", "About 500", "About 5,000", "Over 50,000"],
        "correct": "Fewer than 50",
    },
    explanation="Only a few dozen red wolves live in the wild, all in North Carolina. Zoos like this one breed red wolves to keep the species alive.",
)
ch(
    "cons-macaw",
    "conservation",
    "medium",
    "Wild, Not Pets",
    "What is one of the biggest threats to wild scarlet macaws?",
    animal="scarlet-macaw",
    config={
        "options": ["Being caught for the pet trade", "Too much rain", "Eating too many nuts", "Eagles"],
        "correct": "Being caught for the pet trade",
    },
    explanation="Thousands of parrots are taken from the wild every year to be sold as pets. Choosing captive-bred birds helps protect wild ones.",
)

for i, c in enumerate(challenges, start=1):
    ids[("challenge", c["slug"])] = add(
        "content.challenge",
        i,
        zoo=ZOO,
        slug=c["slug"],
        title=c["title"],
        challenge_type=c["type"],
        difficulty=c["difficulty"],
        xp_reward=c["xp"],
        prompt=c["prompt"],
        hint=c["hint"],
        animal=ids[("animal", c["animal"])] if c["animal"] else None,
        exhibit=ids[("exhibit", c["exhibit"])] if c["exhibit"] else None,
        accept_markers=[ids[("marker", m)] for m in c["accept_markers"]],
        config=c["config"],
        explanation=c["explanation"],
        is_active=True,
    )

# ---------- Badges ----------
badges = [
    (
        "first-steps",
        "First Steps",
        "Scanned your very first quest marker.",
        "🧭",
        "scan_count",
        {"count": 1},
        25,
        False,
    ),
    (
        "giraffe-spotter",
        "Giraffe Spotter",
        "Discovered the giraffe.",
        "🦒",
        "discover_animal",
        {"animal_slugs": ["giraffe"]},
        25,
        False,
    ),
    (
        "savanna-scout",
        "Savanna Scout",
        "Completed the Savanna Safari quest.",
        "🌅",
        "quest_complete",
        {"quest_slug": "savanna-safari"},
        100,
        False,
    ),
    (
        "rainforest-explorer",
        "Rainforest Explorer",
        "Completed the Rainforest Adventure quest.",
        "🌳",
        "quest_complete",
        {"quest_slug": "rainforest-adventure"},
        100,
        False,
    ),
    (
        "master-detective",
        "Master Detective",
        "Completed the Wildlife Detective quest.",
        "🔍",
        "quest_complete",
        {"quest_slug": "wildlife-detective"},
        100,
        False,
    ),
    (
        "reptile-ranger",
        "Reptile Ranger",
        "Discovered every reptile in the zoo.",
        "🐍",
        "discover_count",
        {"count": 2, "tag": "reptile"},
        50,
        False,
    ),
    (
        "conservation-hero",
        "Conservation Hero",
        "Completed 3 conservation challenges.",
        "🌎",
        "challenge_type_count",
        {"challenge_type": "conservation", "count": 3},
        100,
        False,
    ),
    (
        "cartographer",
        "Zoo Cartographer",
        "Scanned a marker in all 5 zones of the zoo.",
        "🗺️",
        "exhibit_count",
        {"count": 5},
        150,
        True,
    ),
]
for i, (slug, name, desc, icon, rtype, rconf, xp, secret) in enumerate(badges, start=1):
    ids[("badge", slug)] = add(
        "content.badge",
        i,
        zoo=ZOO,
        slug=slug,
        name=name,
        description=desc,
        icon=icon,
        rule_type=rtype,
        rule_config=rconf,
        xp_reward=xp,
        is_secret=secret,
        is_active=True,
    )

# ---------- Quests ----------
quests = [
    (
        "savanna-safari",
        "Savanna Safari",
        "Track down the giants of the African Savanna, from the tallest to the loudest.",
        "savanna-scout",
        ["find-giraffe", "who-giraffe", "watch-giraffes", "find-elephant", "cons-elephant", "find-lion"],
        True,
    ),
    (
        "rainforest-adventure",
        "Rainforest Adventure",
        "Follow the trail into the canopy. Something is moving up there. Slowly.",
        "rainforest-explorer",
        ["find-monkey", "colorful-bird", "find-reptile", "sloth-watch", "cons-macaw"],
        True,
    ),
    (
        "wildlife-detective",
        "Wildlife Detective",
        "Riddles, clues and one very rare wolf. Can your team crack every case?",
        "master-detective",
        ["who-elephant", "stripes", "who-python", "hundred-years", "cons-red-wolf", "photo-eating"],
        False,
    ),
]
qc_pk = 1
for i, (slug, name, desc, badge, steps, featured) in enumerate(quests, start=1):
    ids[("quest", slug)] = add(
        "content.quest",
        i,
        zoo=ZOO,
        slug=slug,
        name=name,
        description=desc,
        xp_reward=500,
        badge=ids[("badge", badge)],
        is_active=True,
        is_featured=featured,
        sort_order=i,
        starts_at=None,
        ends_at=None,
        estimated_minutes=25 + 5 * len(steps),
    )
    for order, step in enumerate(steps, start=1):
        add(
            "content.questchallenge",
            qc_pk,
            quest=ids[("quest", slug)],
            challenge=ids[("challenge", step)],
            order=order,
            is_final=(order == len(steps)),
        )
        qc_pk += 1

# ---------- Validation ----------
pks = {}
for row in fx:
    pks.setdefault(row["model"], set()).add(row["pk"])
fk_map = {
    "zoo": "tenants.zoo",
    "exhibit": "content.exhibit",
    "animal": "content.animal",
    "quest": "content.quest",
    "challenge": "content.challenge",
    "badge": "content.badge",
}
errors = []
for row in fx:
    for f, target in fk_map.items():
        v = row["fields"].get(f)
        if v is not None and v not in pks[target]:
            errors.append(f"{row['model']}#{row['pk']}.{f} -> {target}#{v} missing")
    for m in row["fields"].get("accept_markers", []):
        if m not in pks["content.marker"]:
            errors.append(f"{row['model']}#{row['pk']} accept_markers -> marker#{m} missing")
    if row["model"] == "content.challenge":
        t = row["fields"]["challenge_type"]
        cfg = row["fields"]["config"]
        if t in ("animal_hunt", "scavenger") and not row["fields"]["accept_markers"]:
            errors.append(f"challenge {row['fields']['slug']} needs accept_markers")
        if t in ("who_am_i", "conservation") and cfg.get("correct") not in cfg.get("options", []):
            errors.append(f"challenge {row['fields']['slug']} correct answer not in options")
    if row["model"] == "content.badge" and row["fields"]["rule_type"] == "quest_complete":
        if ("quest", row["fields"]["rule_config"]["quest_slug"]) not in ids:
            errors.append(f"badge {row['fields']['slug']} references unknown quest")
codes = [r["fields"]["code"] for r in fx if r["model"] == "content.marker"]
assert len(codes) == len(set(codes)), "duplicate marker codes"
assert not errors, "\n".join(errors)

counts = {m: len(p) for m, p in pks.items()}
with open("cedar_hollow_seed.json", "w") as f:
    json.dump(fx, f, indent=2, ensure_ascii=False)
print(json.dumps(counts, indent=2))

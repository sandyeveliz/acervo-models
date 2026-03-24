#!/usr/bin/env python3
"""
Generate S1 training data for Acervo graph model fine-tuning.

Produces JSONL files with structured training examples for topic classification
and knowledge extraction from conversations.

Usage:
    python 01_dataset/generate_s1_training.py [--seed 42] [--train 500] [--val 50]
"""

import json
import random
import argparse
from pathlib import Path
from copy import deepcopy

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = (
    "You are a knowledge extractor for a personal knowledge graph. "
    "Analyze the conversation and return a single JSON object with "
    "topic classification, entities, relations, and facts. "
    "Output valid JSON only, no markdown, no explanation."
)

OUTPUT_DIR = Path("training_data")

# ═══════════════════════════════════════════════════════════════════════════
# Pools
# ═══════════════════════════════════════════════════════════════════════════

PERSONS = [
    ("alice_chen", "Alice Chen"), ("bob_martinez", "Bob Martinez"),
    ("priya_sharma", "Priya Sharma"), ("james_obrien", "James O'Brien"),
    ("yuki_tanaka", "Yuki Tanaka"), ("maria_rodriguez", "Maria Rodriguez"),
    ("david_kim", "David Kim"), ("sarah_johnson", "Sarah Johnson"),
    ("omar_hassan", "Omar Hassan"), ("nina_petrov", "Nina Petrov"),
    ("luca_rossi", "Luca Rossi"), ("aisha_patel", "Aisha Patel"),
    ("marco_silva", "Marco Silva"), ("elena_volkov", "Elena Volkov"),
    ("raj_kapoor", "Raj Kapoor"), ("carlos_mendez", "Carlos Mendez"),
    ("lisa_wong", "Lisa Wong"), ("ahmed_farid", "Ahmed Farid"),
    ("julia_santos", "Julia Santos"), ("thomas_muller", "Thomas Müller"),
]

PROJECTS = [
    ("beacon", "Beacon"), ("atlas", "Atlas"), ("compass", "Compass"),
    ("nova", "Nova"), ("pulse", "Pulse"), ("orbit", "Orbit"),
    ("forge", "Forge"), ("nexus", "Nexus"), ("helix", "Helix"),
    ("prism", "Prism"), ("zenith", "Zenith"), ("catalyst", "Catalyst"),
    ("horizon", "Horizon"), ("apex", "Apex"), ("vertex_app", "Vertex"),
    ("strato", "Strato"), ("echo_app", "Echo"), ("summit", "Summit"),
    ("flux", "Flux"), ("onyx", "Onyx"),
]

ORGS = [
    ("acme_corp", "Acme Corp"), ("novatech", "NovaTech"),
    ("blueshift_labs", "BlueShift Labs"), ("meridian_software", "Meridian Software"),
    ("pinnacle_digital", "Pinnacle Digital"), ("vertex_solutions", "Vertex Solutions"),
    ("clearpath", "Clearpath"), ("ironforge", "Ironforge"),
    ("skyline_tech", "Skyline Tech"), ("harbor_systems", "Harbor Systems"),
]

FRONTEND = [
    ("react", "React"), ("vue", "Vue"), ("angular", "Angular"),
    ("svelte", "Svelte"), ("nextjs", "Next.js"), ("nuxt", "Nuxt"),
]

BACKEND = [
    ("django", "Django"), ("flask", "Flask"), ("fastapi", "FastAPI"),
    ("express", "Express"), ("spring_boot", "Spring Boot"), ("rails", "Rails"),
]

DATABASES = [
    ("postgresql", "PostgreSQL"), ("mysql", "MySQL"), ("mongodb", "MongoDB"),
    ("redis", "Redis"), ("firebase_db", "Firebase"), ("supabase_db", "Supabase"),
]

CLOUD = [("aws", "AWS"), ("gcp", "GCP"), ("azure", "Azure")]

INFRA = [
    ("docker", "Docker"), ("kubernetes", "Kubernetes"), ("terraform", "Terraform"),
    ("github_actions", "GitHub Actions"), ("jenkins", "Jenkins"),
]

CSS_FW = [("tailwind", "Tailwind CSS"), ("bootstrap", "Bootstrap")]

LANGUAGES = [
    ("typescript", "TypeScript"), ("python_lang", "Python"), ("rust_lang", "Rust"),
    ("go_lang", "Go"), ("java_lang", "Java"), ("kotlin_lang", "Kotlin"),
    ("swift_lang", "Swift"),
]

APP_TYPES_EN = [
    "web app", "mobile app", "SaaS platform", "e-commerce site", "dashboard",
    "API service", "CMS", "marketplace", "analytics platform", "task manager",
    "chat application", "payment gateway", "inventory system",
]
APP_TYPES_ES = [
    "aplicación web", "app mobile", "plataforma SaaS", "e-commerce",
    "dashboard", "servicio de API", "CMS", "marketplace", "plataforma de analytics",
    "gestor de tareas", "sistema de inventario",
]

JOB_TITLES = [
    "frontend developer", "backend developer", "full-stack developer",
    "DevOps engineer", "product manager", "designer", "QA engineer",
    "tech lead", "CTO", "data scientist", "mobile developer", "SRE",
]

# ── Literature pools ──

HP_CHARS = [
    ("harry_potter", "Harry Potter"), ("hermione_granger", "Hermione Granger"),
    ("ron_weasley", "Ron Weasley"), ("dumbledore", "Albus Dumbledore"),
    ("snape", "Severus Snape"), ("voldemort", "Lord Voldemort"),
    ("hagrid", "Rubeus Hagrid"), ("draco_malfoy", "Draco Malfoy"),
    ("sirius_black", "Sirius Black"), ("mcgonagall", "Minerva McGonagall"),
]
HP_PLACES = [
    ("hogwarts", "Hogwarts"), ("diagon_alley", "Diagon Alley"),
    ("forbidden_forest", "Forbidden Forest"), ("privet_drive", "4 Privet Drive"),
    ("hogsmeade", "Hogsmeade"), ("ministry_of_magic", "Ministry of Magic"),
]

LOTR_CHARS = [
    ("frodo", "Frodo Baggins"), ("gandalf", "Gandalf"), ("aragorn", "Aragorn"),
    ("legolas", "Legolas"), ("sauron", "Sauron"), ("gollum", "Gollum"),
    ("samwise", "Samwise Gamgee"), ("gimli", "Gimli"), ("boromir", "Boromir"),
]
LOTR_PLACES = [
    ("mordor", "Mordor"), ("rivendell", "Rivendell"), ("the_shire", "The Shire"),
    ("minas_tirith", "Minas Tirith"), ("isengard", "Isengard"),
]

SW_CHARS = [
    ("luke_skywalker", "Luke Skywalker"), ("darth_vader", "Darth Vader"),
    ("leia_organa", "Leia Organa"), ("han_solo", "Han Solo"),
    ("yoda", "Yoda"), ("obi_wan", "Obi-Wan Kenobi"),
    ("palpatine", "Emperor Palpatine"), ("chewbacca", "Chewbacca"),
]
SW_PLACES = [
    ("tatooine", "Tatooine"), ("coruscant", "Coruscant"),
    ("death_star", "Death Star"), ("hoth", "Hoth"), ("endor", "Endor"),
]

DUNE_CHARS = [
    ("paul_atreides", "Paul Atreides"), ("leto_atreides", "Duke Leto Atreides"),
    ("jessica", "Lady Jessica"), ("baron_harkonnen", "Baron Harkonnen"),
    ("stilgar", "Stilgar"), ("chani", "Chani"), ("duncan_idaho", "Duncan Idaho"),
]
DUNE_PLACES = [("arrakis", "Arrakis"), ("caladan", "Caladan"), ("giedi_prime", "Giedi Prime")]

LIT_UNIVERSES = {
    "hp": (HP_CHARS, HP_PLACES, "Harry Potter"),
    "lotr": (LOTR_CHARS, LOTR_PLACES, "Lord of the Rings"),
    "sw": (SW_CHARS, SW_PLACES, "Star Wars"),
    "dune": (DUNE_CHARS, DUNE_PLACES, "Dune"),
}

# ── Personal pools ──

FAMILY_RELATIONS = [
    "wife", "husband", "partner", "son", "daughter", "brother", "sister",
    "mom", "dad", "uncle", "aunt", "cousin", "grandfather", "grandmother",
]
HOBBIES = [
    "guitar", "painting", "running", "cooking", "photography", "gardening",
    "gaming", "reading", "hiking", "chess", "yoga", "swimming", "cycling",
    "woodworking", "knitting", "baking",
]
CITIES = [
    ("tokyo", "Tokyo"), ("london", "London"), ("new_york", "New York"),
    ("paris", "Paris"), ("buenos_aires", "Buenos Aires"), ("berlin", "Berlin"),
    ("sydney", "Sydney"), ("toronto", "Toronto"), ("barcelona", "Barcelona"),
    ("mexico_city", "Mexico City"), ("bariloche", "Bariloche"),
    ("mendoza", "Mendoza"), ("cordoba_ar", "Córdoba"),
]
FOODS = [
    "risotto", "pasta", "tacos", "sushi", "empanadas", "asado", "pizza",
    "ramen", "curry", "paella", "steak", "pad thai",
]

# ── Academic pools ──

SUBJECTS = [
    ("machine_learning", "Machine Learning"), ("linear_algebra", "Linear Algebra"),
    ("data_structures", "Data Structures"), ("organic_chemistry", "Organic Chemistry"),
    ("microeconomics", "Microeconomics"), ("quantum_physics", "Quantum Physics"),
    ("operating_systems", "Operating Systems"), ("calculus", "Calculus"),
    ("statistics", "Statistics"), ("computer_networks", "Computer Networks"),
]
PROFESSORS = [
    ("prof_zhang", "Professor Zhang"), ("prof_garcia", "Professor García"),
    ("prof_smith", "Professor Smith"), ("prof_kumar", "Professor Kumar"),
    ("prof_williams", "Professor Williams"), ("prof_nakamura", "Professor Nakamura"),
]
ACADEMIC_CONCEPTS = [
    ("backpropagation", "Backpropagation"), ("gradient_descent", "Gradient Descent"),
    ("transformer_arch", "Transformer Architecture"), ("attention_mechanism", "Attention Mechanism"),
    ("overfitting", "Overfitting"), ("regularization", "Regularization"),
    ("eigenvalues", "Eigenvalues"), ("big_o_notation", "Big O Notation"),
    ("turing_machine", "Turing Machine"), ("pagerank", "PageRank"),
]

# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _id(label: str) -> str:
    """Convert a label to a snake_case id."""
    return label.lower().replace(" ", "_").replace("-", "_").replace(".", "").replace("'", "")


def node(nid: str, label: str, ntype: str, layer: str, attributes=None, facts=None, existing_id=None):
    """Build an entity dict for the expected output."""
    return {
        "id": nid,
        "label": label,
        "type": ntype,
        "layer": layer,
        "attributes": attributes or {},
        "facts": facts or [],
        "existing_id": existing_id,
    }


def rel(source: str, target: str, relation: str):
    return {"source": source, "target": target, "relation": relation}


def fact_entry(entity: str, text: str, speaker: str = "user"):
    return {"entity": entity, "text": text, "speaker": speaker}


def existing_node(nid: str, label: str, ntype: str, layer: str, attributes=None):
    """Build a node for existing_nodes (graph state)."""
    return {"id": nid, "label": label, "type": ntype, "layer": layer, "attributes": attributes or {}}


def pick(lst):
    """Pick a random item from a list."""
    return random.choice(lst)


def pick_n(lst, n):
    """Pick n unique random items from a list."""
    return random.sample(lst, min(n, len(lst)))


def pick_hint(scenario: str, topic_label: str = None):
    """Pick a topic_hint appropriate for the scenario."""
    if scenario == "first":
        return "unresolved — classify the topic yourself"
    elif scenario == "same":
        r = random.random()
        if r < 0.5:
            return "same (high confidence from keyword match)"
        elif r < 0.8:
            return "same (high confidence from embedding similarity)"
        else:
            return "unresolved — classify the topic yourself"
    elif scenario == "subtopic":
        r = random.random()
        if r < 0.4 and topic_label:
            return f"subtopic of {topic_label} (medium confidence — verify)"
        else:
            return "unresolved — classify the topic yourself"
    elif scenario == "changed":
        r = random.random()
        if r < 0.4:
            return "changed (medium confidence — verify)"
        else:
            return "unresolved — classify the topic yourself"
    else:
        # query, small_talk, etc.
        r = random.random()
        if r < 0.3:
            return "same (high confidence from keyword match)"
        elif r < 0.5:
            return "same (high confidence from embedding similarity)"
        else:
            return "unresolved — classify the topic yourself"


def format_user_input(existing_nodes, topic_hint, current_topic, prev_assistant, user_msg):
    """Format the user input section of a training example."""
    nodes_json = json.dumps(existing_nodes, ensure_ascii=False) if existing_nodes else "[]"
    topic_str = current_topic if current_topic else "null"
    prev_str = prev_assistant if prev_assistant else "null"
    return (
        f"EXISTING NODES:\n{nodes_json}\n\n"
        f"TOPIC HINT: {topic_hint}\n"
        f"CURRENT TOPIC: {topic_str}\n\n"
        f"PREVIOUS ASSISTANT: {prev_str}\n"
        f"USER: {user_msg}"
    )


def make_example(existing_nodes, topic_hint, current_topic, prev_assistant, user_msg, output):
    """Build a complete training example."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": format_user_input(
                existing_nodes, topic_hint, current_topic, prev_assistant, user_msg
            )},
            {"role": "assistant", "content": json.dumps(output, ensure_ascii=False)},
        ]
    }


def empty_output(action="same", label=None):
    """Return an empty extraction output."""
    topic = {"action": action}
    if label and action != "same":
        topic["label"] = label
    elif action == "same":
        topic["label"] = None
    else:
        topic["label"] = label
    return {"topic": topic, "entities": [], "relations": [], "facts": []}


def spanish_chance():
    """~35% chance to use Spanish."""
    return random.random() < 0.35


# ═══════════════════════════════════════════════════════════════════════════
# Graph State Generators
# ═══════════════════════════════════════════════════════════════════════════

def software_graph(size="small"):
    """Generate a realistic software project graph."""
    proj = pick(PROJECTS)
    org = pick(ORGS)
    fe = pick(FRONTEND)
    be = pick(BACKEND)
    db = pick(DATABASES)
    people = pick_n(PERSONS, random.randint(1, 3) if size == "small" else random.randint(3, 6))

    nodes = [
        existing_node(proj[0], proj[1], "project", "PERSONAL", {"description": f"Internal project at {org[1]}"}),
        existing_node(org[0], org[1], "organization", "PERSONAL"),
        existing_node(fe[0], fe[1], "technology", "UNIVERSAL"),
        existing_node(be[0], be[1], "technology", "UNIVERSAL"),
        existing_node(db[0], db[1], "technology", "UNIVERSAL"),
    ]
    for p in people:
        nodes.append(existing_node(p[0], p[1], "person", "PERSONAL"))

    if size in ("medium", "large"):
        cloud = pick(CLOUD)
        infra = pick(INFRA)
        nodes.append(existing_node(cloud[0], cloud[1], "technology", "UNIVERSAL"))
        nodes.append(existing_node(infra[0], infra[1], "technology", "UNIVERSAL"))
        if size == "large":
            extra_techs = pick_n(LANGUAGES + CSS_FW + INFRA, random.randint(3, 6))
            for t in extra_techs:
                if not any(n["id"] == t[0] for n in nodes):
                    nodes.append(existing_node(t[0], t[1], "technology", "UNIVERSAL"))
            extra_people = pick_n(PERSONS, random.randint(2, 4))
            for p in extra_people:
                if not any(n["id"] == p[0] for n in nodes):
                    nodes.append(existing_node(p[0], p[1], "person", "PERSONAL"))

    return nodes, proj, org, fe, be, db, people


def business_graph(size="small"):
    """Generate a business context graph."""
    org = pick(ORGS)
    people = pick_n(PERSONS, random.randint(2, 4) if size == "small" else random.randint(4, 7))
    client_org = pick([o for o in ORGS if o[0] != org[0]])

    nodes = [
        existing_node(org[0], org[1], "organization", "PERSONAL"),
        existing_node(client_org[0], client_org[1], "organization", "PERSONAL"),
    ]
    for p in people:
        nodes.append(existing_node(p[0], p[1], "person", "PERSONAL"))

    if size in ("medium", "large"):
        proj = pick(PROJECTS)
        nodes.append(existing_node(proj[0], proj[1], "project", "PERSONAL"))
        if size == "large":
            extra_people = pick_n(PERSONS, 4)
            for p in extra_people:
                if not any(n["id"] == p[0] for n in nodes):
                    nodes.append(existing_node(p[0], p[1], "person", "PERSONAL"))
    return nodes, org, client_org, people


def literature_graph(universe_key=None, size="small"):
    """Generate a literature/media graph."""
    if universe_key is None:
        universe_key = pick(list(LIT_UNIVERSES.keys()))
    chars_pool, places_pool, title = LIT_UNIVERSES[universe_key]
    chars = pick_n(chars_pool, random.randint(2, 4) if size == "small" else random.randint(4, 7))
    places = pick_n(places_pool, random.randint(1, 2) if size == "small" else random.randint(2, 4))

    nodes = []
    for c in chars:
        nodes.append(existing_node(c[0], c[1], "person", "UNIVERSAL"))
    for p in places:
        nodes.append(existing_node(p[0], p[1], "place", "UNIVERSAL"))
    return nodes, chars, places, title, universe_key


def personal_graph(size="small"):
    """Generate a personal life graph."""
    family_members = pick_n(PERSONS, random.randint(1, 3) if size == "small" else random.randint(3, 5))
    city = pick(CITIES)
    hobby_names = pick_n(HOBBIES, random.randint(1, 2) if size == "small" else random.randint(2, 4))

    nodes = [existing_node(city[0], city[1], "place", "UNIVERSAL")]
    for p in family_members:
        nodes.append(existing_node(p[0], p[1], "person", "PERSONAL"))
    for h in hobby_names:
        nodes.append(existing_node(_id(h), h.title(), "concept", "UNIVERSAL"))
    return nodes, family_members, city, hobby_names


def academic_graph(size="small"):
    """Generate an academic context graph."""
    subject = pick(SUBJECTS)
    prof = pick(PROFESSORS)
    concepts = pick_n(ACADEMIC_CONCEPTS, random.randint(1, 3) if size == "small" else random.randint(3, 5))

    nodes = [
        existing_node(subject[0], subject[1], "concept", "UNIVERSAL"),
        existing_node(prof[0], prof[1], "person", "PERSONAL"),
    ]
    for c in concepts:
        nodes.append(existing_node(c[0], c[1], "concept", "UNIVERSAL"))
    if size in ("medium", "large"):
        extra_subj = pick_n(SUBJECTS, 2)
        for s in extra_subj:
            if not any(n["id"] == s[0] for n in nodes):
                nodes.append(existing_node(s[0], s[1], "concept", "UNIVERSAL"))
    return nodes, subject, prof, concepts


# ═══════════════════════════════════════════════════════════════════════════
# Scenario Generators
# ═══════════════════════════════════════════════════════════════════════════


# ─── 1. First Message / Empty Graph ───────────────────────────────────────

def gen_first_message_software():
    proj = pick(PROJECTS)
    org = pick(ORGS)
    fe = pick(FRONTEND)
    be = pick(BACKEND)
    db = pick(DATABASES)
    person = pick(PERSONS)
    app_type = pick(APP_TYPES_EN)

    templates = [
        f"I'm working on {proj[1]}, a {app_type} built with {fe[1]} and {be[1]}. We're using {db[1]} for the database. The team lead is {person[1]}.",
        f"Hey, let me tell you about our project {proj[1]}. It's a {app_type} we're building at {org[1]}. Stack is {be[1]} + {fe[1]}, {db[1]} for storage. {person[1]} is the tech lead.",
        f"Starting a new project called {proj[1]}. It's going to be a {app_type}. We picked {fe[1]} for the frontend, {be[1]} for the API, and {db[1]}. I work at {org[1]}.",
        f"So we just kicked off {proj[1]} at {org[1]}. It's a {app_type}. We're going with {be[1]} on the backend, {fe[1]} on the frontend, and {db[1]}. {person[1]} is handling the frontend.",
        f"I need to talk about {proj[1]}. We're building this {app_type} for {org[1]}. The stack is {be[1]}, {fe[1]}, and {db[1]}. {person[1]} just joined the team as {pick(JOB_TITLES)}.",
    ]
    templates_es = [
        f"Estoy trabajando en {proj[1]}, una {pick(APP_TYPES_ES)} con {fe[1]} y {be[1]}. Usamos {db[1]} para la base de datos. {person[1]} es el tech lead.",
        f"Te cuento del proyecto {proj[1]}. Es una {pick(APP_TYPES_ES)} que estamos armando en {org[1]}. Stack: {be[1]} + {fe[1]}, base de datos en {db[1]}.",
        f"Arrancamos {proj[1]} en {org[1]}. Es una {pick(APP_TYPES_ES)}. Vamos con {be[1]}, {fe[1]} y {db[1]}. {person[1]} maneja el frontend.",
    ]

    msg = pick(templates_es) if spanish_chance() else pick(templates)

    entities = [
        node(proj[0], proj[1], "project", "PERSONAL"),
        node(org[0], org[1], "organization", "PERSONAL"),
        node(fe[0], fe[1], "technology", "UNIVERSAL"),
        node(be[0], be[1], "technology", "UNIVERSAL"),
        node(db[0], db[1], "technology", "UNIVERSAL"),
        node(person[0], person[1], "person", "PERSONAL"),
    ]
    relations = [
        rel(proj[0], org[0], "part_of"),
        rel(proj[0], fe[0], "uses_technology"),
        rel(proj[0], be[0], "uses_technology"),
        rel(proj[0], db[0], "uses_technology"),
        rel(person[0], org[0], "works_at"),
        rel(person[0], proj[0], "maintains"),
    ]
    output = {
        "topic": {"action": "changed", "label": f"{proj[1]} development"},
        "entities": entities,
        "relations": relations,
        "facts": [],
    }
    return make_example([], "unresolved — classify the topic yourself", None, None, msg, output)


def gen_first_message_business():
    org = pick(ORGS)
    client = pick([o for o in ORGS if o[0] != org[0]])
    people = pick_n(PERSONS, random.randint(2, 3))
    roles = pick_n(JOB_TITLES, len(people))

    templates = [
        f"I work at {org[1]}. Our main client right now is {client[1]}. The team includes {people[0][1]} ({roles[0]}) and {people[1][1]} ({roles[1]}).",
        f"Let me give you some context. I'm at {org[1]}, we're working with {client[1]} on a big project. {people[0][1]} is our {roles[0]} and {people[1][1]} handles {roles[1]} stuff.",
        f"Hey, I'm part of the team at {org[1]}. We have a client called {client[1]}. Key people: {people[0][1]} is {roles[0]}, {people[1][1]} is {roles[1]}.",
    ]
    templates_es = [
        f"Trabajo en {org[1]}. Nuestro cliente principal ahora es {client[1]}. El equipo incluye a {people[0][1]} ({roles[0]}) y {people[1][1]} ({roles[1]}).",
        f"Te pongo en contexto. Estoy en {org[1]}, trabajamos con {client[1]}. {people[0][1]} es {roles[0]} y {people[1][1]} es {roles[1]}.",
    ]

    msg = pick(templates_es) if spanish_chance() else pick(templates)

    entities = [
        node(org[0], org[1], "organization", "PERSONAL"),
        node(client[0], client[1], "organization", "PERSONAL"),
    ]
    relations_list = [rel(org[0], client[0], "serves")]
    for i, p in enumerate(people):
        entities.append(node(p[0], p[1], "person", "PERSONAL",
                             facts=[{"text": f"Works as {roles[i]}", "speaker": "user"}]))
        relations_list.append(rel(p[0], org[0], "works_at"))

    output = {
        "topic": {"action": "changed", "label": f"{org[1]} team"},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example([], "unresolved — classify the topic yourself", None, None, msg, output)


def gen_first_message_literature():
    ukey = pick(list(LIT_UNIVERSES.keys()))
    chars_pool, places_pool, title = LIT_UNIVERSES[ukey]
    chars = pick_n(chars_pool, random.randint(2, 4))
    place = pick(places_pool)

    templates = [
        f"I've been reading {title}. The main characters so far are {', '.join(c[1] for c in chars)}. The story takes place in {place[1]}.",
        f"Let's talk about {title}. I'm really into {chars[0][1]} and {chars[1][1]} right now. The setting in {place[1]} is amazing.",
        f"I just started {title}. So far I've met {chars[0][1]}, {chars[1][1]}, and they're at {place[1]}.",
        f"Can we discuss {title}? I want to track the characters: {', '.join(c[1] for c in chars)}. Currently they're at {place[1]}.",
    ]
    templates_es = [
        f"Estoy leyendo {title}. Los personajes principales son {', '.join(c[1] for c in chars)}. La historia pasa en {place[1]}.",
        f"Hablemos de {title}. Me enganché con {chars[0][1]} y {chars[1][1]}. {place[1]} es un escenario increíble.",
    ]

    msg = pick(templates_es) if spanish_chance() else pick(templates)
    entities = [node(c[0], c[1], "person", "UNIVERSAL") for c in chars]
    entities.append(node(place[0], place[1], "place", "UNIVERSAL"))
    relations_list = [rel(c[0], place[0], "located_in") for c in chars]

    output = {
        "topic": {"action": "changed", "label": title},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example([], "unresolved — classify the topic yourself", None, None, msg, output)


def gen_first_message_personal():
    family = pick_n(PERSONS, random.randint(1, 2))
    city = pick(CITIES)
    relation_type = pick(FAMILY_RELATIONS[:4])  # close family
    hobby = pick(HOBBIES)

    templates = [
        f"A bit about me: I live in {city[1]} with my {relation_type} {family[0][1]}. I've been getting into {hobby} lately.",
        f"Hey, I'm based in {city[1]}. My {relation_type} is {family[0][1]}. In my free time I do {hobby}.",
        f"Let me introduce myself. I'm from {city[1]}, my {relation_type} {family[0][1]} and I live there. I'm really into {hobby}.",
    ]
    templates_es = [
        f"Vivo en {city[1]} con mi {relation_type} {family[0][1]}. Últimamente estoy metido en {hobby}.",
        f"Te cuento un poco: soy de {city[1]}, mi {relation_type} es {family[0][1]}. Me gusta mucho {hobby}.",
    ]

    msg = pick(templates_es) if spanish_chance() else pick(templates)
    hobby_id = _id(hobby)
    entities = [
        node(family[0][0], family[0][1], "person", "PERSONAL",
             facts=[{"text": f"Is the user's {relation_type}", "speaker": "user"}]),
        node(city[0], city[1], "place", "UNIVERSAL"),
        node(hobby_id, hobby.title(), "concept", "UNIVERSAL"),
    ]
    relations_list = [
        rel(family[0][0], city[0], "located_in"),
    ]
    output = {
        "topic": {"action": "changed", "label": "Personal life"},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example([], "unresolved — classify the topic yourself", None, None, msg, output)


def gen_first_message_academic():
    subject = pick(SUBJECTS)
    prof = pick(PROFESSORS)
    concept = pick(ACADEMIC_CONCEPTS)

    templates = [
        f"I'm taking {subject[1]} this semester with {prof[1]}. We just started covering {concept[1]}.",
        f"This semester I'm enrolled in {subject[1]}. {prof[1]} is teaching it. So far we've covered {concept[1]}.",
        f"Hey, I need help with my {subject[1]} course. {prof[1]} is the professor. We're learning about {concept[1]} right now.",
    ]
    templates_es = [
        f"Este semestre estoy cursando {subject[1]} con {prof[1]}. Estamos viendo {concept[1]}.",
        f"Estoy en el curso de {subject[1]}. Lo da {prof[1]}. Ahora estamos con {concept[1]}.",
    ]

    msg = pick(templates_es) if spanish_chance() else pick(templates)
    entities = [
        node(subject[0], subject[1], "concept", "UNIVERSAL"),
        node(prof[0], prof[1], "person", "PERSONAL"),
        node(concept[0], concept[1], "concept", "UNIVERSAL"),
    ]
    relations_list = [
        rel(concept[0], subject[0], "part_of"),
    ]
    output = {
        "topic": {"action": "changed", "label": f"{subject[1]} course"},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example([], "unresolved — classify the topic yourself", None, None, msg, output)


# ─── 2. Same Topic, New Facts ─────────────────────────────────────────────

def gen_same_facts_software():
    g = software_graph(pick(["small", "medium"]))
    nodes, proj, org, fe, be, db, people = g
    person = pick(people) if people else pick(PERSONS)
    topic = f"{proj[1]} development"
    hint = pick_hint("same", topic)

    fact_templates = [
        (proj[0], f"Has {random.randint(1000, 100000)} monthly active users"),
        (proj[0], f"Launched in {pick(['January', 'February', 'March', 'April', 'May', 'June'])} {pick([2024, 2025, 2026])}"),
        (proj[0], f"Currently in {pick(['alpha', 'beta', 'production', 'staging'])}"),
        (proj[0], f"The team has {random.randint(3, 15)} developers"),
        (fe[0], f"Using version {random.randint(14, 19)}.{random.randint(0, 9)}"),
        (person[0], f"Has been on the project for {random.randint(1, 24)} months"),
        (person[0], f"Is responsible for the {pick(['auth', 'payments', 'notifications', 'search', 'dashboard'])} module"),
        (db[0], f"Has {random.randint(10, 500)} tables"),
        (org[0], f"Has {random.randint(10, 200)} employees"),
    ]
    selected_facts = pick_n(fact_templates, random.randint(1, 3))

    messages_en = [
        f"By the way, {selected_facts[0][1].lower()}." if len(selected_facts) == 1
        else f"Some updates: {'. '.join(f[1] for f in selected_facts)}.",
        f"Oh, I forgot to mention — {selected_facts[0][1].lower()}.",
        f"Quick update on {proj[1]}: {'. '.join(f[1] for f in selected_facts)}.",
        f"Just so you know, {selected_facts[0][1].lower()}." + (f" Also, {selected_facts[1][1].lower()}." if len(selected_facts) > 1 else ""),
    ]
    messages_es = [
        f"Ah, me olvidé de decirte: {selected_facts[0][1].lower()}.",
        f"Un update de {proj[1]}: {'. '.join(f[1] for f in selected_facts)}.",
        f"Para que sepas, {selected_facts[0][1].lower()}.",
    ]

    msg = pick(messages_es) if spanish_chance() else pick(messages_en)
    prev = pick([
        f"Got it, so {proj[1]} uses {be[1]} and {fe[1]}.",
        f"Thanks for the context about {proj[1]}.",
        f"I see, {proj[1]} is built with {fe[1]}.",
        None,
    ])

    facts_output = [fact_entry(f[0], f[1]) for f in selected_facts]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": [],
        "relations": [],
        "facts": facts_output,
    }
    return make_example(nodes, hint, topic, prev, msg, output)


def gen_same_facts_business():
    g = business_graph(pick(["small", "medium"]))
    nodes, org, client, people = g
    topic = f"{org[1]} team"
    hint = pick_hint("same", topic)
    person = pick(people)

    fact_templates = [
        (org[0], f"Revenue grew {random.randint(5, 40)}% last quarter"),
        (org[0], f"Has {random.randint(20, 500)} employees"),
        (client[0], f"Contract is worth ${random.randint(10, 500)}k"),
        (client[0], f"Been a client for {random.randint(1, 5)} years"),
        (person[0], f"Got promoted to {pick(JOB_TITLES)}"),
        (person[0], f"Is leading the {pick(['Q1', 'Q2', 'Q3', 'Q4'])} initiative"),
    ]
    selected = pick_n(fact_templates, random.randint(1, 2))

    msg_en = [
        f"Oh, {selected[0][1].lower()}.",
        f"Update: {'. '.join(f[1] for f in selected)}.",
        f"I should mention that {selected[0][1].lower()}.",
    ]
    msg_es = [
        f"Ah, {selected[0][1].lower()}.",
        f"Te cuento que {selected[0][1].lower()}.",
    ]

    msg = pick(msg_es) if spanish_chance() else pick(msg_en)
    output = {
        "topic": {"action": "same", "label": None},
        "entities": [],
        "relations": [],
        "facts": [fact_entry(f[0], f[1]) for f in selected],
    }
    return make_example(nodes, hint, topic, f"Tell me more about {org[1]}.", msg, output)


def gen_same_facts_literature():
    g = literature_graph(size=pick(["small", "medium"]))
    nodes, chars, places, title, ukey = g
    topic = title
    hint = pick_hint("same", topic)
    char = pick(chars)

    fact_templates = [
        (char[0], f"Is described as {pick(['brave', 'cunning', 'wise', 'loyal', 'mysterious', 'powerful'])}"),
        (char[0], f"Has a special ability: {pick(['magic', 'the Force', 'precognition', 'sword fighting'])}"),
        (char[0], f"Motivation is to {pick(['save the world', 'gain power', 'protect friends', 'find the truth', 'seek revenge'])}"),
        (places[0][0], f"Is described as {pick(['ancient', 'dangerous', 'beautiful', 'hidden', 'massive'])}"),
    ]
    selected = pick_n(fact_templates, random.randint(1, 2))

    msg = pick([
        f"So in the book, {selected[0][1].lower()}.",
        f"I noticed that {char[1]} — {selected[0][1].lower()}.",
        f"In {title}, {selected[0][1].lower()}.",
    ])

    output = {
        "topic": {"action": "same", "label": None},
        "entities": [],
        "relations": [],
        "facts": [fact_entry(f[0], f[1]) for f in selected],
    }
    return make_example(nodes, hint, topic, f"What else about {title}?", msg, output)


def gen_same_facts_personal():
    g = personal_graph(pick(["small", "medium"]))
    nodes, family, city, hobbies = g
    topic = "Personal life"
    hint = pick_hint("same", topic)
    person = pick(family)

    fact_templates = [
        (person[0], f"Works as a {pick(['teacher', 'engineer', 'doctor', 'lawyer', 'designer', 'accountant'])}"),
        (person[0], f"Birthday is in {pick(['January', 'March', 'June', 'August', 'November'])}"),
        (city[0], f"The commute is {random.randint(10, 60)} minutes"),
        (city[0], f"Great {pick(['food scene', 'parks', 'nightlife', 'public transport'])}"),
    ]
    selected = pick_n(fact_templates, random.randint(1, 2))

    msg = pick([
        f"By the way, {selected[0][1].lower()}.",
        f"Oh I forgot, {selected[0][1].lower()}.",
        f"Also, {selected[0][1].lower()}.",
    ])

    output = {
        "topic": {"action": "same", "label": None},
        "entities": [],
        "relations": [],
        "facts": [fact_entry(f[0], f[1]) for f in selected],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_same_facts_academic():
    g = academic_graph(pick(["small", "medium"]))
    nodes, subject, prof, concepts = g
    topic = f"{subject[1]} course"
    hint = pick_hint("same", topic)
    concept = pick(concepts) if concepts else pick(ACADEMIC_CONCEPTS)

    fact_templates = [
        (subject[0], f"The midterm is {pick(['next week', 'in two weeks', 'on Friday'])}"),
        (subject[0], f"Uses {pick(['Python', 'MATLAB', 'R', 'Julia'])} for assignments"),
        (prof[0], f"Has office hours on {pick(['Monday', 'Wednesday', 'Thursday'])}s"),
        (prof[0], f"Published a paper on {concept[1].lower()}"),
        (concept[0], f"Key formula involves {pick(['matrices', 'derivatives', 'integrals', 'probability distributions'])}"),
    ]
    selected = pick_n(fact_templates, random.randint(1, 2))

    msg = pick([
        f"Oh yeah, {selected[0][1].lower()}.",
        f"About the course: {selected[0][1].lower()}.",
        f"I should add that {selected[0][1].lower()}.",
    ])

    output = {
        "topic": {"action": "same", "label": None},
        "entities": [],
        "relations": [],
        "facts": [fact_entry(f[0], f[1]) for f in selected],
    }
    return make_example(nodes, hint, topic, None, msg, output)


# ─── 3. Same Topic, New Entities ──────────────────────────────────────────

def gen_same_new_entities_software():
    g = software_graph(pick(["small", "medium"]))
    nodes, proj, org, fe, be, db, people = g
    topic = f"{proj[1]} development"
    hint = pick_hint("same", topic)

    new_tech = pick([t for t in INFRA + CLOUD + CSS_FW + LANGUAGES if not any(n["id"] == t[0] for n in nodes)])
    new_person = pick([p for p in PERSONS if not any(n["id"] == p[0] for n in nodes)])
    role = pick(JOB_TITLES)

    templates = [
        f"We also added {new_tech[1]} to the stack, and {new_person[1]} just joined as {role}.",
        f"{new_person[1]} started this week as our new {role}. Oh, and we're now using {new_tech[1]}.",
        f"New update: we integrated {new_tech[1]} into {proj[1]}. Also, {new_person[1]} is our new {role}.",
        f"We brought in {new_person[1]} as {role} and started using {new_tech[1]} for the project.",
    ]
    templates_es = [
        f"Sumamos {new_tech[1]} al stack, y {new_person[1]} se unió como {role}.",
        f"{new_person[1]} arrancó esta semana como {role}. Y ahora usamos {new_tech[1]}.",
    ]

    msg = pick(templates_es) if spanish_chance() else pick(templates)
    entities = [
        node(new_tech[0], new_tech[1], "technology", "UNIVERSAL"),
        node(new_person[0], new_person[1], "person", "PERSONAL",
             facts=[{"text": f"Works as {role}", "speaker": "user"}]),
    ]
    relations_list = [
        rel(proj[0], new_tech[0], "uses_technology"),
        rel(new_person[0], proj[0], "maintains"),
        rel(new_person[0], org[0], "works_at"),
    ]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example(nodes, hint, topic, f"Got it, tell me more about {proj[1]}.", msg, output)


def gen_same_new_entities_business():
    g = business_graph("small")
    nodes, org, client, people = g
    topic = f"{org[1]} team"
    hint = pick_hint("same", topic)

    new_person = pick([p for p in PERSONS if not any(n["id"] == p[0] for n in nodes)])
    new_proj = pick(PROJECTS)
    role = pick(JOB_TITLES)

    msg = pick([
        f"We're also starting {new_proj[1]}, a new initiative. {new_person[1]} will lead it as {role}.",
        f"{new_person[1]} is joining the team as {role} to work on {new_proj[1]}.",
        f"New project: {new_proj[1]}. {new_person[1]} ({role}) is heading it up.",
    ])

    entities = [
        node(new_proj[0], new_proj[1], "project", "PERSONAL"),
        node(new_person[0], new_person[1], "person", "PERSONAL",
             facts=[{"text": f"Works as {role}", "speaker": "user"}]),
    ]
    relations_list = [
        rel(new_proj[0], org[0], "part_of"),
        rel(new_person[0], new_proj[0], "maintains"),
        rel(new_person[0], org[0], "works_at"),
    ]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_same_new_entities_literature():
    g = literature_graph(size="small")
    nodes, chars, places, title, ukey = g
    topic = title
    hint = pick_hint("same", topic)
    chars_pool, places_pool, _ = LIT_UNIVERSES[ukey]

    new_chars = [c for c in chars_pool if not any(n["id"] == c[0] for n in nodes)]
    if not new_chars:
        new_chars = [("new_character", "A New Character")]
    new_char = pick(new_chars)
    existing_char = pick(chars)

    msg = pick([
        f"There's also {new_char[1]} who appears in the story. They interact with {existing_char[1]} a lot.",
        f"I just got to the part where {new_char[1]} shows up. Seems connected to {existing_char[1]}.",
        f"New character: {new_char[1]}. They seem to have a history with {existing_char[1]}.",
    ])

    entities = [node(new_char[0], new_char[1], "person", "UNIVERSAL")]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": entities,
        "relations": [rel(new_char[0], existing_char[0], "part_of")],
        "facts": [],
    }
    return make_example(nodes, hint, topic, f"Tell me more about {title}.", msg, output)


def gen_same_new_entities_personal():
    g = personal_graph("small")
    nodes, family, city, hobbies = g
    topic = "Personal life"
    hint = pick_hint("same", topic)

    new_person = pick([p for p in PERSONS if not any(n["id"] == p[0] for n in nodes)])
    relation = pick(FAMILY_RELATIONS)

    msg = pick([
        f"Oh, and my {relation} {new_person[1]} lives nearby too.",
        f"I should mention my {relation} {new_person[1]}.",
        f"My {relation} is {new_person[1]}, they live in {city[1]} too.",
    ])

    entities = [
        node(new_person[0], new_person[1], "person", "PERSONAL",
             facts=[{"text": f"Is the user's {relation}", "speaker": "user"}]),
    ]
    relations_list = [rel(new_person[0], city[0], "located_in")]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_same_new_entities_academic():
    g = academic_graph("small")
    nodes, subject, prof, concepts = g
    topic = f"{subject[1]} course"
    hint = pick_hint("same", topic)

    new_concept = pick([c for c in ACADEMIC_CONCEPTS if not any(n["id"] == c[0] for n in nodes)])

    msg = pick([
        f"We just started learning about {new_concept[1]} in class.",
        f"{prof[1]} introduced {new_concept[1]} today. It's connected to what we studied before.",
        f"New topic in {subject[1]}: {new_concept[1]}.",
    ])

    entities = [node(new_concept[0], new_concept[1], "concept", "UNIVERSAL")]
    relations_list = [rel(new_concept[0], subject[0], "part_of")]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


# ─── 4. Subtopic Shift ───────────────────────────────────────────────────

def gen_subtopic_software():
    g = software_graph(pick(["small", "medium"]))
    nodes, proj, org, fe, be, db, people = g
    parent_topic = f"{proj[1]} development"
    hint = pick_hint("subtopic", parent_topic)
    subtopic = pick(["authentication", "payments", "notifications", "database schema",
                      "API design", "deployment", "testing", "CI/CD pipeline",
                      "caching layer", "search functionality"])

    templates = [
        f"Let's dive into the {subtopic} part of {proj[1]}.",
        f"Now about the {subtopic} specifically — how should we handle it?",
        f"I want to focus on the {subtopic} module. That's where we have issues.",
        f"Can we talk about the {subtopic} for {proj[1]}?",
        f"The {subtopic} is the next thing I need to figure out.",
    ]
    templates_es = [
        f"Vamos con la parte de {subtopic} de {proj[1]}.",
        f"Ahora quiero hablar del {subtopic} específicamente.",
        f"Enfoquémonos en el módulo de {subtopic}.",
    ]

    msg = pick(templates_es) if spanish_chance() else pick(templates)
    output = {
        "topic": {"action": "subtopic", "label": f"{proj[1]} {subtopic}"},
        "entities": [],
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, parent_topic, f"What else about {proj[1]}?", msg, output)


def gen_subtopic_business():
    g = business_graph("medium")
    nodes, org, client, people = g
    parent_topic = f"{org[1]} team"
    hint = pick_hint("subtopic", parent_topic)
    aspect = pick(["hiring plan", "Q3 budget", "client onboarding", "team restructure",
                    "performance reviews", "new office", "remote policy"])

    msg = pick([
        f"About the {aspect} — where are we on that?",
        f"Let's focus on the {aspect} now.",
        f"I need to discuss the {aspect} specifically.",
    ])

    output = {
        "topic": {"action": "subtopic", "label": aspect.title()},
        "entities": [],
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, parent_topic, None, msg, output)


def gen_subtopic_literature():
    g = literature_graph(size="medium")
    nodes, chars, places, title, ukey = g
    parent_topic = title
    hint = pick_hint("subtopic", parent_topic)
    char = pick(chars)

    msg = pick([
        f"Let's focus on {char[1]}'s backstory specifically.",
        f"I want to dig deeper into {char[1]}'s character arc.",
        f"What about {char[1]}'s motivations? Let's explore that.",
        f"Can we analyze {char[1]} in more detail?",
    ])

    output = {
        "topic": {"action": "subtopic", "label": f"{char[1]}'s character"},
        "entities": [],
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, parent_topic, f"What would you like to know about {title}?", msg, output)


def gen_subtopic_personal():
    g = personal_graph("medium")
    nodes, family, city, hobbies = g
    parent_topic = "Personal life"
    hint = pick_hint("subtopic", parent_topic)
    hobby = pick(hobbies)

    msg = pick([
        f"Let me tell you more about my {hobby} specifically.",
        f"About the {hobby} thing — I've been making progress.",
        f"Can we focus on my {hobby} goals?",
    ])

    output = {
        "topic": {"action": "subtopic", "label": f"{hobby.title()} hobby"},
        "entities": [],
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, parent_topic, None, msg, output)


def gen_subtopic_academic():
    g = academic_graph("medium")
    nodes, subject, prof, concepts = g
    parent_topic = f"{subject[1]} course"
    hint = pick_hint("subtopic", parent_topic)
    concept = pick(concepts)

    msg = pick([
        f"Let's dive deeper into {concept[1]}. I'm struggling with it.",
        f"Can we focus on {concept[1]}? The lecture was confusing.",
        f"I need to understand {concept[1]} better for the exam.",
    ])

    output = {
        "topic": {"action": "subtopic", "label": concept[1]},
        "entities": [],
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, parent_topic, None, msg, output)


# ─── 5. Topic Change ─────────────────────────────────────────────────────

def gen_topic_change_sw_to_personal():
    g = software_graph("small")
    nodes = g[0]
    proj = g[1]
    old_topic = f"{proj[1]} development"
    hint = pick_hint("changed")

    hobby = pick(HOBBIES)
    city = pick(CITIES)

    templates = [
        f"Switching gears — I went to {city[1]} last weekend. Amazing trip.",
        f"Completely different topic: I started {hobby} recently.",
        f"Bueno, cambiando de tema. Fui a {city[1]} el finde. Increíble.",
        f"Anyway, enough about work. I've been getting into {hobby} lately.",
        f"Off topic — have you been to {city[1]}? I just got back.",
    ]

    msg = pick(templates)
    entities = [node(city[0], city[1], "place", "UNIVERSAL")]
    output = {
        "topic": {"action": "changed", "label": "Travel"},
        "entities": entities,
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, old_topic, f"Anything else about {proj[1]}?", msg, output)


def gen_topic_change_personal_to_sw():
    g = personal_graph("small")
    nodes = g[0]
    old_topic = "Personal life"
    hint = pick_hint("changed")

    proj = pick(PROJECTS)
    tech = pick(FRONTEND + BACKEND)

    templates = [
        f"OK, let's talk about work. I need to set up {proj[1]} with {tech[1]}.",
        f"Volvamos al trabajo. Necesito armar {proj[1]} con {tech[1]}.",
        f"Back to coding — I'm starting {proj[1]}, using {tech[1]}.",
        f"Different topic: {proj[1]}. We're building it with {tech[1]}.",
    ]

    msg = pick(templates)
    entities = [
        node(proj[0], proj[1], "project", "PERSONAL"),
        node(tech[0], tech[1], "technology", "UNIVERSAL"),
    ]
    output = {
        "topic": {"action": "changed", "label": f"{proj[1]} development"},
        "entities": entities,
        "relations": [rel(proj[0], tech[0], "uses_technology")],
        "facts": [],
    }
    return make_example(nodes, hint, old_topic, None, msg, output)


def gen_topic_change_sw_to_literature():
    g = software_graph("small")
    nodes = g[0]
    proj = g[1]
    old_topic = f"{proj[1]} development"
    hint = pick_hint("changed")

    ukey = pick(list(LIT_UNIVERSES.keys()))
    chars_pool, places_pool, title = LIT_UNIVERSES[ukey]
    char = pick(chars_pool)

    templates = [
        f"Hey, completely off topic — have you read {title}? I love {char[1]}.",
        f"Bueno, cambiando de tema — estoy leyendo {title}. {char[1]} es genial.",
        f"Random question: what do you think about {char[1]} in {title}?",
        f"Moving on from work — I just started reading {title}.",
    ]

    msg = pick(templates)
    entities = [node(char[0], char[1], "person", "UNIVERSAL")]
    output = {
        "topic": {"action": "changed", "label": title},
        "entities": entities,
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, old_topic, None, msg, output)


def gen_topic_change_literature_to_academic():
    g = literature_graph(size="small")
    nodes = g[0]
    title = g[3]
    old_topic = title
    hint = pick_hint("changed")

    subject = pick(SUBJECTS)
    prof = pick(PROFESSORS)

    msg = pick([
        f"OK, I need to study now. I have {subject[1]} with {prof[1]} tomorrow.",
        f"Changing topics — {subject[1]} exam is coming up. {prof[1]}'s class.",
        f"Enough about {title}. I need to prep for {subject[1]}.",
    ])

    entities = [
        node(subject[0], subject[1], "concept", "UNIVERSAL"),
        node(prof[0], prof[1], "person", "PERSONAL"),
    ]
    output = {
        "topic": {"action": "changed", "label": f"{subject[1]} course"},
        "entities": entities,
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, old_topic, None, msg, output)


def gen_topic_change_generic():
    """Generic topic change between any two domains."""
    domains = ["software", "business", "personal", "academic"]
    from_domain = pick(domains)

    if from_domain == "software":
        g = software_graph("small")
        nodes, old_topic = g[0], f"{g[1][1]} development"
    elif from_domain == "business":
        g = business_graph("small")
        nodes, old_topic = g[0], f"{g[1][1]} team"
    elif from_domain == "personal":
        g = personal_graph("small")
        nodes, old_topic = g[0], "Personal life"
    else:
        g = academic_graph("small")
        nodes, old_topic = g[0], f"{g[1][1]} course"

    hint = pick_hint("changed")

    # Simple topic change with minimal entity extraction
    new_topics = [
        ("I need to plan a trip to {city}.", lambda c: (
            [node(c[0], c[1], "place", "UNIVERSAL")], [], "Travel planning")),
        ("My friend {person} asked me for help with something.", lambda p: (
            [node(p[0], p[1], "person", "PERSONAL")], [], "Helping a friend")),
        ("Have you heard about {tech}? I'm curious about it.", lambda t: (
            [node(t[0], t[1], "technology", "UNIVERSAL")], [], f"Learning {t[1]}")),
    ]

    choice = pick(new_topics)
    if "city" in choice[0]:
        city = pick(CITIES)
        msg = choice[0].format(city=city[1])
        ents, rels, label = choice[1](city)
    elif "person" in choice[0]:
        person = pick(PERSONS)
        msg = choice[0].format(person=person[1])
        ents, rels, label = choice[1](person)
    else:
        tech = pick(FRONTEND + BACKEND + LANGUAGES)
        msg = choice[0].format(tech=tech[1])
        ents, rels, label = choice[1](tech)

    output = {
        "topic": {"action": "changed", "label": label},
        "entities": ents,
        "relations": rels,
        "facts": [],
    }
    return make_example(nodes, hint, old_topic, None, msg, output)


# ─── 6. Query / Question (Empty extraction) ──────────────────────────────

def gen_query_software():
    g = software_graph(pick(["small", "medium", "large"]))
    nodes, proj, org, fe, be, db, people = g
    topic = f"{proj[1]} development"
    hint = pick_hint("query", topic)

    templates = [
        f"What framework are we using for the frontend of {proj[1]} again?",
        f"Who's the tech lead on {proj[1]}?",
        f"Can you remind me what database {proj[1]} uses?",
        f"How does the {pick(['auth', 'caching', 'search'])} module work in {proj[1]}?",
        f"What's the deploy process for {proj[1]}?",
        f"Is {fe[1]} still the right choice for the frontend?",
        f"Should we consider {pick(DATABASES)[1]} instead of {db[1]}?",
    ]
    templates_es = [
        f"Qué framework usamos en el frontend de {proj[1]}?",
        f"Quién es el tech lead de {proj[1]}?",
        f"Me recordás qué base de datos usa {proj[1]}?",
        f"Cómo funciona el módulo de {pick(['auth', 'pagos', 'búsqueda'])} en {proj[1]}?",
    ]

    msg = pick(templates_es) if spanish_chance() else pick(templates)
    output = empty_output("same")
    return make_example(nodes, hint, topic, None, msg, output)


def gen_query_business():
    g = business_graph(pick(["small", "medium"]))
    nodes, org, client, people = g
    topic = f"{org[1]} team"
    hint = pick_hint("query", topic)

    person = pick(people)
    msg = pick([
        f"What's {person[1]}'s role again?",
        f"When did we start working with {client[1]}?",
        f"How many people are on the team?",
        f"What's the budget for the {client[1]} project?",
    ])

    output = empty_output("same")
    return make_example(nodes, hint, topic, None, msg, output)


def gen_query_literature():
    g = literature_graph(size=pick(["small", "medium"]))
    nodes, chars, places, title, ukey = g
    topic = title
    hint = pick_hint("query", topic)
    char = pick(chars)

    msg = pick([
        f"What happened to {char[1]} after the battle?",
        f"Where is {pick(places)[1]} in relation to the main setting?",
        f"Who are {char[1]}'s allies?",
        f"What's the significance of {pick(places)[1]}?",
    ])

    output = empty_output("same")
    return make_example(nodes, hint, topic, None, msg, output)


def gen_query_personal():
    g = personal_graph(pick(["small", "medium"]))
    nodes, family, city, hobbies = g
    topic = "Personal life"
    hint = pick_hint("query", topic)

    msg = pick([
        f"What was that restaurant in {city[1]} we talked about?",
        f"When did I say I started {pick(hobbies)}?",
        f"What neighborhood do I live in?",
    ])

    output = empty_output("same")
    return make_example(nodes, hint, topic, None, msg, output)


def gen_query_academic():
    g = academic_graph(pick(["small", "medium"]))
    nodes, subject, prof, concepts = g
    topic = f"{subject[1]} course"
    hint = pick_hint("query", topic)

    msg = pick([
        f"When is the {subject[1]} midterm?",
        f"What did {prof[1]} say about the homework?",
        f"Can you explain {pick(concepts)[1]} again?",
    ])

    output = empty_output("same")
    return make_example(nodes, hint, topic, None, msg, output)


# ─── 7. Small Talk / Meta (Always empty) ─────────────────────────────────

def gen_small_talk():
    graph_options = [
        [],
        software_graph("small")[0],
        business_graph("small")[0],
        personal_graph("small")[0],
    ]
    nodes = pick(graph_options)
    topic = pick(["Some project", "Personal life", "Work", None])
    hint = pick_hint("query", topic)

    messages = [
        "Thanks!", "Got it.", "OK, sounds good.", "Perfect.",
        "Gracias!", "Dale.", "Entendido.", "Perfecto.",
        "Can you repeat that?", "I see.", "Makes sense.",
        "OK let me think about that.", "Right.", "Agreed.",
        "Sure, let's do that.", "That works for me.",
        "No worries.", "All good.", "Yep.", "Nope, that's it.",
        "Cool.", "Nice.", "Great.", "Awesome.",
        "Buenísimo.", "Joya.", "Listo.", "Genial.",
        "Hmm, interesting.", "Let me check.", "One sec.",
        "Actually, never mind.", "Forget it, it's fine.",
        "Thanks for the help!", "Gracias por la ayuda!",
        "Bye!", "Nos vemos!", "Talk later.", "Hablamos.",
    ]

    msg = pick(messages)
    prev = pick([
        "Here's what I found about that.", "Let me know if you need anything else.",
        "I've updated the information.", None,
    ])

    output = empty_output("same")
    return make_example(nodes, hint, topic, prev, msg, output)


# ─── 8. Dedup / Existing Reference ───────────────────────────────────────

def gen_dedup_software():
    g = software_graph(pick(["small", "medium"]))
    nodes, proj, org, fe, be, db, people = g
    topic = f"{proj[1]} development"
    hint = pick_hint("same", topic)

    # User refers to existing entity by different name
    dedup_patterns = [
        (proj[0], proj[1], [
            f"Our project is almost done with the migration.",
            f"The app needs a new feature in the dashboard.",
            f"Our product has been getting good feedback.",
        ]),
        (db[0], db[1], [
            f"The database is running slow on production.",
            f"We need to optimize the DB queries.",
            f"La base de datos está lenta en producción.",
        ]),
        (fe[0], fe[1], [
            f"The frontend framework needs an update.",
            f"Our UI library is a version behind.",
        ]),
    ]

    pattern = pick(dedup_patterns)
    entity_id, entity_label, msgs = pattern
    msg = pick(msgs)

    alias_labels = {
        proj[0]: pick(["our project", "the app", "our product", "the platform"]),
        db[0]: pick(["the database", "the DB", "la base de datos"]),
        fe[0]: pick(["the frontend framework", "our UI library"]),
    }
    alias = alias_labels.get(entity_id, "it")
    alias_id = _id(alias)

    entities = [node(alias_id, alias.title(), "technology" if entity_id in (db[0], fe[0]) else "project",
                      "PERSONAL", existing_id=entity_id)]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": entities,
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_dedup_business():
    g = business_graph("medium")
    nodes, org, client, people = g
    topic = f"{org[1]} team"
    hint = pick_hint("same", topic)
    person = pick(people)

    patterns = [
        (client[0], pick([f"The client wants a meeting this week.", f"Nuestro cliente quiere una reunión."]),
         pick(["the client", "el cliente"]), "organization"),
        (org[0], pick([f"Our company just got new funding.", f"La empresa consiguió nueva financiación."]),
         pick(["our company", "la empresa"]), "organization"),
        (person[0], pick([f"The team lead is taking PTO next week.", f"El lead se toma vacaciones."]),
         pick(["the team lead", "el lead"]), "person"),
    ]

    pattern = pick(patterns)
    entity_id, msg, alias, ntype = pattern
    alias_id = _id(alias)

    entities = [node(alias_id, alias.title(), ntype, "PERSONAL", existing_id=entity_id)]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": entities,
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_dedup_literature():
    g = literature_graph(size="medium")
    nodes, chars, places, title, ukey = g
    topic = title
    hint = pick_hint("same", topic)
    char = pick(chars)

    # Refer to character by description
    aliases = {
        "harry_potter": ("the boy who lived", "The Boy Who Lived"),
        "hermione_granger": ("the brightest witch", "The Brightest Witch"),
        "dumbledore": ("the headmaster", "The Headmaster"),
        "gandalf": ("the wizard", "The Wizard"),
        "frodo": ("the ring bearer", "The Ring Bearer"),
        "aragorn": ("the ranger", "The Ranger"),
        "luke_skywalker": ("the young jedi", "The Young Jedi"),
        "darth_vader": ("the dark lord", "The Dark Lord"),
        "paul_atreides": ("the chosen one", "The Chosen One"),
    }

    if char[0] in aliases:
        alias_id, alias_label = aliases[char[0]]
        alias_id = _id(alias_id)
    else:
        alias_id, alias_label = _id(f"the hero"), "The Hero"

    msg = pick([
        f"So {alias_label.lower()} finally confronted the enemy.",
        f"I think {alias_label.lower()} made a mistake in that scene.",
        f"The part where {alias_label.lower()} reveals the truth was amazing.",
    ])

    entities = [node(alias_id, alias_label, "person", "UNIVERSAL", existing_id=char[0])]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": entities,
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_dedup_personal():
    g = personal_graph("small")
    nodes, family, city, hobbies = g
    topic = "Personal life"
    hint = pick_hint("same", topic)
    person = pick(family)
    relation = pick(FAMILY_RELATIONS[:4])

    msg = pick([
        f"My {relation} said we should go to the park this weekend.",
        f"Mi {relation} quiere ir al parque el fin de semana.",
    ])

    alias_id = _id(f"my {relation}")
    entities = [node(alias_id, f"My {relation.title()}", "person", "PERSONAL", existing_id=person[0])]
    output = {
        "topic": {"action": "same", "label": None},
        "entities": entities,
        "relations": [],
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


# ─── 9. Correction / Update ──────────────────────────────────────────────

def gen_correction_software():
    g = software_graph(pick(["small", "medium"]))
    nodes, proj, org, fe, be, db, people = g
    topic = f"{proj[1]} development"
    hint = pick_hint("same", topic)

    new_tech = pick([t for t in FRONTEND + BACKEND + DATABASES if t[0] != fe[0] and t[0] != be[0] and t[0] != db[0]])

    correction_patterns = [
        (f"Actually, we switched from {fe[1]} to {new_tech[1]} for the frontend.",
         [node(new_tech[0], new_tech[1], "technology", "UNIVERSAL")],
         [rel(proj[0], new_tech[0], "uses_technology")],
         [fact_entry(proj[0], f"Migrated frontend from {fe[1]} to {new_tech[1]}")]),
        (f"Correction: {people[0][1]} left the company. {pick([p for p in PERSONS if p not in people])[1]} replaced them.",
         [],
         [],
         [fact_entry(people[0][0], "Left the company")]),
        (f"Actually, the project is called {pick(PROJECTS)[1]} now, we rebranded.",
         [],
         [],
         [fact_entry(proj[0], "Was recently rebranded")]),
        (f"We're not using {db[1]} anymore, we migrated to {new_tech[1]}.",
         [node(new_tech[0], new_tech[1], "technology", "UNIVERSAL")],
         [rel(proj[0], new_tech[0], "uses_technology")],
         [fact_entry(proj[0], f"Migrated from {db[1]} to {new_tech[1]}")]),
    ]
    correction_patterns_es = [
        (f"En realidad, cambiamos de {fe[1]} a {new_tech[1]} en el frontend.",
         [node(new_tech[0], new_tech[1], "technology", "UNIVERSAL")],
         [rel(proj[0], new_tech[0], "uses_technology")],
         [fact_entry(proj[0], f"Migrated frontend from {fe[1]} to {new_tech[1]}")]),
        (f"Corrección: ya no usamos {db[1]}, migramos a {new_tech[1]}.",
         [node(new_tech[0], new_tech[1], "technology", "UNIVERSAL")],
         [rel(proj[0], new_tech[0], "uses_technology")],
         [fact_entry(proj[0], f"Migrated from {db[1]} to {new_tech[1]}")]),
    ]

    if spanish_chance():
        pattern = pick(correction_patterns_es)
    else:
        pattern = pick(correction_patterns)

    msg, ents, rels, facts = pattern
    output = {
        "topic": {"action": "same", "label": None},
        "entities": ents,
        "relations": rels,
        "facts": facts,
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_correction_business():
    g = business_graph("small")
    nodes, org, client, people = g
    topic = f"{org[1]} team"
    hint = pick_hint("same", topic)
    person = pick(people)
    new_role = pick(JOB_TITLES)

    msg = pick([
        f"Actually, {person[1]} got promoted to {new_role}.",
        f"Correction: {person[1]} is now {new_role}, not what I said before.",
        f"Update: {person[1]} moved to the {new_role} position.",
    ])

    output = {
        "topic": {"action": "same", "label": None},
        "entities": [],
        "relations": [],
        "facts": [fact_entry(person[0], f"Now works as {new_role}")],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_correction_personal():
    g = personal_graph("small")
    nodes, family, city, hobbies = g
    topic = "Personal life"
    hint = pick_hint("same", topic)
    person = pick(family)

    new_city = pick([c for c in CITIES if c[0] != city[0]])
    msg = pick([
        f"Actually, we moved to {new_city[1]} last month.",
        f"Correction — {person[1]} changed jobs. They're now a {pick(['nurse', 'architect', 'chef', 'consultant'])}.",
        f"Oh wait, I gave you wrong info. We're in {new_city[1]} now, not {city[1]}.",
    ])

    output = {
        "topic": {"action": "same", "label": None},
        "entities": [],
        "relations": [],
        "facts": [fact_entry(person[0] if "job" in msg.lower() else city[0],
                             msg.split("—")[-1].strip() if "—" in msg else f"Relocated to {new_city[1]}")],
    }
    return make_example(nodes, hint, topic, None, msg, output)


# ─── 10. Event Extraction ────────────────────────────────────────────────

def gen_event_software():
    g = software_graph(pick(["small", "medium"]))
    nodes, proj, org, fe, be, db, people = g
    topic = f"{proj[1]} development"
    hint = pick_hint("same", topic)

    event_types = [
        ("sprint_review", "Sprint Review", f"Reviewed {pick(['Q1', 'Q2', 'Q3', 'Q4'])} deliverables"),
        ("production_deploy", "Production Deploy", f"Deployed {proj[1]} v{random.randint(1,5)}.{random.randint(0,9)} to production"),
        ("incident", "Production Incident", f"Outage in {proj[1]} {pick(['auth', 'API', 'database', 'payments'])} module"),
        ("code_review", "Code Review Session", f"Reviewed PR for {pick(['auth', 'payments', 'search', 'notifications'])} feature"),
        ("planning_meeting", "Planning Meeting", f"Planned the next sprint for {proj[1]}"),
    ]
    event = pick(event_types)
    participants = pick_n(people, min(random.randint(2, 3), len(people)))
    temporal = pick(["last Monday", "yesterday", "this morning", "last Friday", "two days ago",
                      "el lunes pasado", "ayer", "esta mañana"])

    templates = [
        f"We had a {event[1].lower()} {temporal}. {', '.join(p[1] for p in participants)} were there. {event[2]}.",
        f"{temporal.capitalize()}, we did a {event[1].lower()} with {' and '.join(p[1] for p in participants)}. {event[2]}.",
        f"The {event[1].lower()} happened {temporal}. Participants: {', '.join(p[1] for p in participants)}. {event[2]}.",
    ]

    msg = pick(templates)
    event_node = node(event[0], event[1], "event", "PERSONAL",
                       attributes={"description": event[2], "temporal_marker": temporal})
    relations_list = [rel(p[0], event[0], "participated_in") for p in participants]

    output = {
        "topic": {"action": "same", "label": None},
        "entities": [event_node],
        "relations": relations_list,
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_event_business():
    g = business_graph("medium")
    nodes, org, client, people = g
    topic = f"{org[1]} team"
    hint = pick_hint("same", topic)

    event_types = [
        ("client_meeting", "Client Meeting", f"Met with {client[1]} to discuss requirements"),
        ("board_meeting", "Board Meeting", f"Discussed {pick(['Q1', 'Q2', 'Q3', 'Q4'])} results"),
        ("hiring_interview", "Interview Session", f"Interviewed candidates for {pick(JOB_TITLES)} position"),
        ("quarterly_review", "Quarterly Review", f"Reviewed performance and set goals"),
    ]
    event = pick(event_types)
    participants = pick_n(people, min(random.randint(2, 3), len(people)))
    temporal = pick(["this morning", "yesterday", "last week", "on Monday"])

    msg = f"We had a {event[1].lower()} {temporal} with {' and '.join(p[1] for p in participants)}. {event[2]}."

    event_node = node(event[0], event[1], "event", "PERSONAL",
                       attributes={"description": event[2], "temporal_marker": temporal})
    relations_list = [rel(p[0], event[0], "participated_in") for p in participants]

    output = {
        "topic": {"action": "same", "label": None},
        "entities": [event_node],
        "relations": relations_list,
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_event_literature():
    g = literature_graph(size="medium")
    nodes, chars, places, title, ukey = g
    topic = title
    hint = pick_hint("same", topic)

    participants = pick_n(chars, min(random.randint(2, 3), len(chars)))
    place = pick(places)

    events_by_universe = {
        "hp": [
            ("battle_of_hogwarts", "Battle of Hogwarts", "Final battle against Voldemort's forces"),
            ("triwizard_tournament", "Triwizard Tournament", "Dangerous magical competition between schools"),
            ("quidditch_match", "Quidditch Match", "Flying broomstick sporting event"),
            ("sorting_ceremony", "Sorting Ceremony", "New students sorted into houses"),
        ],
        "lotr": [
            ("battle_helms_deep", "Battle of Helm's Deep", "Massive siege battle against Saruman's army"),
            ("council_of_elrond", "Council of Elrond", "Meeting to decide the fate of the Ring"),
            ("destruction_ring", "Destruction of the Ring", "The One Ring is destroyed in Mount Doom"),
        ],
        "sw": [
            ("battle_yavin", "Battle of Yavin", "Rebel attack on the Death Star"),
            ("battle_hoth", "Battle of Hoth", "Imperial assault on Rebel base"),
            ("jedi_training", "Jedi Training", "Luke trains with Yoda on Dagobah"),
        ],
        "dune": [
            ("battle_arrakeen", "Battle of Arrakeen", "Harkonnen attack on Atreides forces"),
            ("riding_sandworm", "Sandworm Ride", "Paul rides a sandworm for the first time"),
            ("water_of_life", "Water of Life Ceremony", "Paul drinks the Water of Life"),
        ],
    }

    event_pool = events_by_universe.get(ukey, events_by_universe["hp"])
    event = pick(event_pool)
    temporal = pick(["chapter 5", "in the middle of the book", "near the end", "early in the story",
                      "after the betrayal", "during the war"])

    msg = pick([
        f"The part where {event[1]} happens is incredible. {', '.join(p[1] for p in participants)} are all involved. It takes place at {place[1]}.",
        f"In {title}, {event[2].lower()}. {' and '.join(p[1] for p in participants)} participate. Happens at {place[1]}, {temporal}.",
        f"Let's talk about {event[1]} — {event[2].lower()}. Key characters: {', '.join(p[1] for p in participants)}.",
    ])

    event_node = node(event[0], event[1], "event", "UNIVERSAL",
                       attributes={"description": event[2], "temporal_marker": temporal})
    relations_list = [rel(p[0], event[0], "participated_in") for p in participants]
    relations_list.append(rel(event[0], place[0], "located_in"))

    output = {
        "topic": {"action": "same", "label": None},
        "entities": [event_node],
        "relations": relations_list,
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


def gen_event_personal():
    g = personal_graph("small")
    nodes, family, city, hobbies = g
    topic = "Personal life"
    hint = pick_hint("same", topic)

    participants = family[:min(2, len(family))]
    event_types = [
        ("birthday_party", "Birthday Party", f"Celebrated at a restaurant in {city[1]}"),
        ("family_trip", "Family Trip", f"Traveled together for a weekend"),
        ("dinner_party", "Dinner Party", f"Hosted dinner with friends and family"),
        ("graduation", "Graduation", f"Ceremony at the local university"),
    ]
    event = pick(event_types)
    temporal = pick(["last Saturday", "two weeks ago", "last month", "el sábado pasado"])

    msg = f"We had {event[1].lower()} {temporal}. {' and '.join(p[1] for p in participants)} were there. {event[2]}."

    event_node = node(event[0], event[1], "event", "PERSONAL",
                       attributes={"description": event[2], "temporal_marker": temporal})
    relations_list = [rel(p[0], event[0], "participated_in") for p in participants]

    output = {
        "topic": {"action": "same", "label": None},
        "entities": [event_node],
        "relations": relations_list,
        "facts": [],
    }
    return make_example(nodes, hint, topic, None, msg, output)


# ─── 11. File/Document Indexing ───────────────────────────────────────────

def gen_document_software():
    proj = pick(PROJECTS)
    people = pick_n(PERSONS, random.randint(1, 3))
    techs = pick_n(FRONTEND + BACKEND + DATABASES, random.randint(2, 4))
    topic = f"{proj[1]} development"

    doc_types = [
        (f"{proj[0]}_architecture_doc", f"{proj[1]} Architecture Document", "document",
         f"Architecture overview of {proj[1]}. Tech stack: {', '.join(t[1] for t in techs)}. "
         f"Key contributors: {', '.join(p[1] for p in people)}."),
        (f"{proj[0]}_meeting_notes", f"{proj[1]} Meeting Notes", "document",
         f"Meeting notes for {proj[1]} sprint planning. "
         f"Attendees: {', '.join(p[1] for p in people)}. Discussed migration to {techs[0][1]}."),
    ]
    doc = pick(doc_types)

    msg = f"Here's a summary of the document I just read:\n\n{doc[3]}"
    prev = "I've processed the document. Here's what I found:"

    entities = [
        node(proj[0], proj[1], "project", "PERSONAL"),
    ]
    for t in techs:
        entities.append(node(t[0], t[1], "technology", "UNIVERSAL"))
    for p in people:
        entities.append(node(p[0], p[1], "person", "PERSONAL"))

    entities.append(node(doc[0], doc[1], doc[2], "PERSONAL",
                          attributes={"description": doc[3][:100]}))

    relations_list = [rel(proj[0], t[0], "uses_technology") for t in techs]
    relations_list.append(rel(doc[0], proj[0], "documented_in"))
    for p in people:
        relations_list.append(rel(p[0], proj[0], "maintains"))

    output = {
        "topic": {"action": "changed", "label": topic},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    # Use empty graph for document indexing (fresh context)
    return make_example([], "unresolved — classify the topic yourself", None, prev, msg, output)


def gen_document_literature():
    ukey = pick(list(LIT_UNIVERSES.keys()))
    chars_pool, places_pool, title = LIT_UNIVERSES[ukey]
    chars = pick_n(chars_pool, random.randint(2, 4))
    place = pick(places_pool)

    chapter = random.randint(1, 20)
    msg = (
        f"Summary of {title}, Chapter {chapter}:\n\n"
        f"{chars[0][1]} travels to {place[1]} where they encounter {chars[1][1]}. "
        f"A conflict arises when "
        f"{pick(['an ancient prophecy', 'a hidden enemy', 'a mysterious artifact', 'a betrayal'])} "
        f"is revealed. {chars[0][1]} must decide whether to "
        f"{pick(['fight', 'flee', 'negotiate', 'sacrifice'])}."
    )

    event_id = _id(f"chapter_{chapter}_conflict")
    entities = [node(c[0], c[1], "person", "UNIVERSAL") for c in chars]
    entities.append(node(place[0], place[1], "place", "UNIVERSAL"))
    entities.append(node(event_id, f"Chapter {chapter} Conflict", "event", "UNIVERSAL",
                          attributes={"description": f"Conflict at {place[1]}", "temporal_marker": f"Chapter {chapter}"}))

    relations_list = [rel(c[0], event_id, "participated_in") for c in chars[:2]]
    relations_list.append(rel(event_id, place[0], "located_in"))

    output = {
        "topic": {"action": "changed", "label": title},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example([], "unresolved — classify the topic yourself", None,
                        "Here's the chapter summary:", msg, output)


def gen_document_academic():
    subject = pick(SUBJECTS)
    concepts = pick_n(ACADEMIC_CONCEPTS, random.randint(2, 3))
    people = pick_n(PROFESSORS, random.randint(1, 2))

    paper_title = f"A Survey of {concepts[0][1]} in {subject[1]}"
    msg = (
        f"Summary of the paper \"{paper_title}\":\n\n"
        f"This paper reviews {concepts[0][1]} and its relationship to {concepts[1][1] if len(concepts) > 1 else subject[1]}. "
        f"Authors: {', '.join(p[1] for p in people)}. "
        f"Key finding: {pick(['improved accuracy by 15%', 'reduced complexity', 'novel approach to the problem', 'state-of-the-art results'])}."
    )

    doc_id = _id(paper_title[:40])
    entities = [
        node(doc_id, paper_title, "document", "UNIVERSAL"),
    ]
    for c in concepts:
        entities.append(node(c[0], c[1], "concept", "UNIVERSAL"))
    for p in people:
        entities.append(node(p[0], p[1], "person", "UNIVERSAL"))

    relations_list = [rel(doc_id, c[0], "documented_in") for c in concepts]
    for p in people:
        relations_list.append(rel(p[0], doc_id, "created_by"))

    output = {
        "topic": {"action": "changed", "label": f"{subject[1]} research"},
        "entities": entities,
        "relations": relations_list,
        "facts": [],
    }
    return make_example([], "unresolved — classify the topic yourself", None,
                        "Here's a summary of the paper:", msg, output)


# ═══════════════════════════════════════════════════════════════════════════
# Distribution Table
# ═══════════════════════════════════════════════════════════════════════════

# (generator_function, count)
# Total should be ~500 for training
DISTRIBUTION = [
    # 1. First message / empty graph (40)
    (gen_first_message_software, 14),
    (gen_first_message_business, 8),
    (gen_first_message_literature, 6),
    (gen_first_message_personal, 6),
    (gen_first_message_academic, 6),

    # 2. Same topic, new facts (80)
    (gen_same_facts_software, 28),
    (gen_same_facts_business, 16),
    (gen_same_facts_literature, 12),
    (gen_same_facts_personal, 12),
    (gen_same_facts_academic, 12),

    # 3. Same topic, new entities (60)
    (gen_same_new_entities_software, 21),
    (gen_same_new_entities_business, 12),
    (gen_same_new_entities_literature, 9),
    (gen_same_new_entities_personal, 9),
    (gen_same_new_entities_academic, 9),

    # 4. Subtopic shift (50)
    (gen_subtopic_software, 18),
    (gen_subtopic_business, 10),
    (gen_subtopic_literature, 8),
    (gen_subtopic_personal, 7),
    (gen_subtopic_academic, 7),

    # 5. Topic change (50)
    (gen_topic_change_sw_to_personal, 10),
    (gen_topic_change_personal_to_sw, 10),
    (gen_topic_change_sw_to_literature, 8),
    (gen_topic_change_literature_to_academic, 7),
    (gen_topic_change_generic, 15),

    # 6. Query / question (50)
    (gen_query_software, 18),
    (gen_query_business, 10),
    (gen_query_literature, 8),
    (gen_query_personal, 7),
    (gen_query_academic, 7),

    # 7. Small talk / meta (30) — padded to ~80 empty total with queries
    (gen_small_talk, 30),

    # 8. Dedup / existing reference (40)
    (gen_dedup_software, 14),
    (gen_dedup_business, 10),
    (gen_dedup_literature, 8),
    (gen_dedup_personal, 8),

    # 9. Correction / update (30)
    (gen_correction_software, 14),
    (gen_correction_business, 8),
    (gen_correction_personal, 8),

    # 10. Event extraction (40)
    (gen_event_software, 12),
    (gen_event_business, 8),
    (gen_event_literature, 12),
    (gen_event_personal, 8),

    # 11. File/document indexing (30)
    (gen_document_software, 12),
    (gen_document_literature, 10),
    (gen_document_academic, 8),
]


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def validate_example(example: dict) -> bool:
    """Validate that a training example is well-formed."""
    try:
        assert len(example["messages"]) == 3
        assert example["messages"][0]["role"] == "system"
        assert example["messages"][1]["role"] == "user"
        assert example["messages"][2]["role"] == "assistant"
        # Validate the assistant output is valid JSON
        output = json.loads(example["messages"][2]["content"])
        assert "topic" in output
        assert "entities" in output
        assert "relations" in output
        assert "facts" in output
        assert output["topic"]["action"] in ("same", "subtopic", "changed")
        # Validate entity types
        valid_types = {"person", "organization", "project", "technology", "place", "event", "document", "concept"}
        for ent in output["entities"]:
            assert ent["type"] in valid_types, f"Invalid type: {ent['type']}"
        # Validate relation types
        valid_rels = {
            "part_of", "created_by", "maintains", "works_at", "member_of",
            "uses_technology", "depends_on", "alternative_to",
            "located_in", "deployed_on", "produces", "serves", "documented_in",
            "participated_in", "triggered_by", "resulted_in",
        }
        for r in output["relations"]:
            assert r["relation"] in valid_rels, f"Invalid relation: {r['relation']}"
        return True
    except (json.JSONDecodeError, AssertionError, KeyError) as e:
        print(f"  Validation error: {e}")
        return False


def generate(n_train: int = 500, n_val: int = 50, seed: int = 42):
    """Generate training and validation datasets."""
    random.seed(seed)

    # Calculate total from distribution
    total_dist = sum(count for _, count in DISTRIBUTION)
    print(f"Distribution total: {total_dist} examples")

    # Generate all examples
    all_examples = []
    for gen_fn, count in DISTRIBUTION:
        for _ in range(count):
            try:
                example = gen_fn()
                all_examples.append(example)
            except Exception as e:
                print(f"  Error in {gen_fn.__name__}: {e}")

    # Validate all examples
    print(f"Generated {len(all_examples)} examples. Validating...")
    valid = []
    invalid_count = 0
    for ex in all_examples:
        if validate_example(ex):
            valid.append(ex)
        else:
            invalid_count += 1

    print(f"Valid: {len(valid)}, Invalid: {invalid_count}")

    # Shuffle
    random.shuffle(valid)

    # Split train/val
    val_size = min(n_val, len(valid) // 10)
    val_examples = valid[:val_size]
    train_examples = valid[val_size:]

    # Trim to requested sizes
    if len(train_examples) > n_train:
        train_examples = train_examples[:n_train]

    # Write files
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_path = OUTPUT_DIR / "s1_extraction.jsonl"
    with open(train_path, "w", encoding="utf-8") as f:
        for ex in train_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(train_examples)} training examples to {train_path}")

    val_path = OUTPUT_DIR / "s1_validation.jsonl"
    with open(val_path, "w", encoding="utf-8") as f:
        for ex in val_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(val_examples)} validation examples to {val_path}")

    # Print distribution stats
    print("\n--- Distribution Stats ---")
    train_outputs = [json.loads(ex["messages"][2]["content"]) for ex in train_examples]

    actions = {"same": 0, "subtopic": 0, "changed": 0}
    empty_count = 0
    for o in train_outputs:
        actions[o["topic"]["action"]] += 1
        if not o["entities"] and not o["facts"]:
            empty_count += 1

    total = len(train_outputs)
    print(f"topic_action distribution:")
    for a, c in actions.items():
        print(f"  {a}: {c} ({c/total*100:.1f}%)")
    print(f"Empty extractions: {empty_count} ({empty_count/total*100:.1f}%)")

    # Check JSON parse rate
    parse_ok = 0
    for ex in train_examples + val_examples:
        try:
            json.loads(ex["messages"][2]["content"])
            parse_ok += 1
        except json.JSONDecodeError:
            pass
    total_all = len(train_examples) + len(val_examples)
    print(f"JSON parse rate: {parse_ok}/{total_all} ({parse_ok/total_all*100:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate S1 training data")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train", type=int, default=500)
    parser.add_argument("--val", type=int, default=50)
    args = parser.parse_args()

    generate(n_train=args.train, n_val=args.val, seed=args.seed)

"""
Clean and update existing training data for v3 dataset.

1. Replace copyrighted IP (Harry Potter, LOTR, Star Wars, Dune) with public domain equivalents
2. Update S1_SYSTEM_PROMPT in ALL examples to the new version (with Facts section)

Usage:
    python clean_and_update_dataset.py
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from schema import S1_SYSTEM_PROMPT, validate_s1

# ---------------------------------------------------------------------------
# Public Domain Character/Place Pools (replacements for copyrighted IP)
# ---------------------------------------------------------------------------

# Harry Potter → Sherlock Holmes (Arthur Conan Doyle, public domain)
SHERLOCK_CHARS = [
    ("sherlock_holmes", "Sherlock Holmes"),
    ("dr_watson", "Dr. Watson"),
    ("mrs_hudson", "Mrs. Hudson"),
    ("inspector_lestrade", "Inspector Lestrade"),
    ("professor_moriarty", "Professor Moriarty"),
    ("irene_adler", "Irene Adler"),
    ("mycroft_holmes", "Mycroft Holmes"),
    ("colonel_moran", "Colonel Moran"),
    ("mary_morstan", "Mary Morstan"),
    ("inspector_gregson", "Inspector Gregson"),
]

SHERLOCK_PLACES = [
    ("baker_street", "221B Baker Street"),
    ("scotland_yard", "Scotland Yard"),
    ("reichenbach_falls", "Reichenbach Falls"),
    ("baskerville_hall", "Baskerville Hall"),
    ("diogenes_club", "The Diogenes Club"),
    ("london", "London"),
]

# Lord of the Rings → Don Quijote (Miguel de Cervantes, public domain)
QUIJOTE_CHARS = [
    ("don_quijote", "Don Quijote"),
    ("sancho_panza", "Sancho Panza"),
    ("dulcinea", "Dulcinea del Toboso"),
    ("rocinante", "Rocinante"),
    ("cura_perez", "El Cura Pero Pérez"),
    ("barbero_nicolas", "Maese Nicolás"),
    ("cardenio", "Cardenio"),
    ("dorotea", "Dorotea"),
    ("duque", "El Duque"),
]

QUIJOTE_PLACES = [
    ("la_mancha", "La Mancha"),
    ("toboso", "El Toboso"),
    ("venta", "La Venta"),
    ("sierra_morena", "Sierra Morena"),
    ("barcelona", "Barcelona"),
]

# Star Wars → La Odisea (Homer, public domain)
ODISEA_CHARS = [
    ("odiseo", "Odiseo"),
    ("penelope", "Penélope"),
    ("telemachus", "Telémaco"),
    ("athena", "Atenea"),
    ("poseidon", "Poseidón"),
    ("circe", "Circe"),
    ("polyphemus", "Polifemo"),
    ("calypso", "Calipso"),
]

ODISEA_PLACES = [
    ("ithaca", "Ítaca"),
    ("troy", "Troya"),
    ("olympus", "Olimpo"),
    ("isle_of_circe", "Isla de Circe"),
    ("underworld", "Inframundo"),
]

# Dune → Frankenstein / Drácula (Shelley / Stoker, public domain)
GOTHIC_CHARS = [
    ("victor_frankenstein", "Victor Frankenstein"),
    ("the_creature", "The Creature"),
    ("elizabeth_lavenza", "Elizabeth Lavenza"),
    ("henry_clerval", "Henry Clerval"),
    ("count_dracula", "Count Dracula"),
    ("jonathan_harker", "Jonathan Harker"),
    ("mina_harker", "Mina Harker"),
]

GOTHIC_PLACES = [
    ("geneva", "Geneva"),
    ("ingolstadt", "Ingolstadt"),
    ("castle_dracula", "Castle Dracula"),
]

# ---------------------------------------------------------------------------
# Replacement Mappings
# ---------------------------------------------------------------------------

# Map old (copyrighted) → new (public domain) character IDs and labels
HP_TO_SHERLOCK = {
    # Characters (id → id)
    "harry_potter": "sherlock_holmes",
    "hermione_granger": "dr_watson",
    "ron_weasley": "mrs_hudson",
    "dumbledore": "mycroft_holmes",
    "albus_dumbledore": "mycroft_holmes",
    "snape": "professor_moriarty",
    "severus_snape": "professor_moriarty",
    "voldemort": "colonel_moran",
    "lord_voldemort": "colonel_moran",
    "hagrid": "inspector_lestrade",
    "rubeus_hagrid": "inspector_lestrade",
    "draco_malfoy": "irene_adler",
    "sirius_black": "mary_morstan",
    "mcgonagall": "inspector_gregson",
    "minerva_mcgonagall": "inspector_gregson",
    # Places
    "hogwarts": "baker_street",
    "diagon_alley": "scotland_yard",
    "forbidden_forest": "reichenbach_falls",
    "privet_drive": "baskerville_hall",
    "4_privet_drive": "baskerville_hall",
    "hogsmeade": "diogenes_club",
    "ministry_of_magic": "london",
}

HP_LABEL_MAP = {
    "Harry Potter": "Sherlock Holmes",
    "Hermione Granger": "Dr. Watson",
    "Ron Weasley": "Mrs. Hudson",
    "Albus Dumbledore": "Mycroft Holmes",
    "Dumbledore": "Mycroft Holmes",
    "Severus Snape": "Professor Moriarty",
    "Snape": "Professor Moriarty",
    "Lord Voldemort": "Colonel Moran",
    "Voldemort": "Colonel Moran",
    "Rubeus Hagrid": "Inspector Lestrade",
    "Hagrid": "Inspector Lestrade",
    "Draco Malfoy": "Irene Adler",
    "Sirius Black": "Mary Morstan",
    "Minerva McGonagall": "Inspector Gregson",
    "McGonagall": "Inspector Gregson",
    "Hogwarts": "221B Baker Street",
    "Diagon Alley": "Scotland Yard",
    "Forbidden Forest": "Reichenbach Falls",
    "4 Privet Drive": "Baskerville Hall",
    "Privet Drive": "Baskerville Hall",
    "Hogsmeade": "The Diogenes Club",
    "Ministry of Magic": "London",
    "Harry Potter series": "Sherlock Holmes stories",
    "Harry Potter universe": "Sherlock Holmes stories",
}

LOTR_TO_QUIJOTE = {
    "frodo": "don_quijote",
    "frodo_baggins": "don_quijote",
    "gandalf": "cura_perez",
    "aragorn": "cardenio",
    "legolas": "barbero_nicolas",
    "sauron": "duque",
    "gollum": "rocinante",
    "samwise": "sancho_panza",
    "samwise_gamgee": "sancho_panza",
    "gimli": "dorotea",
    "boromir": "dulcinea",
    "mordor": "sierra_morena",
    "rivendell": "la_mancha",
    "the_shire": "toboso",
    "minas_tirith": "barcelona",
    "isengard": "venta",
}

LOTR_LABEL_MAP = {
    "Frodo Baggins": "Don Quijote",
    "Frodo": "Don Quijote",
    "Gandalf": "El Cura Pero Pérez",
    "Aragorn": "Cardenio",
    "Legolas": "Maese Nicolás",
    "Sauron": "El Duque",
    "Gollum": "Rocinante",
    "Samwise Gamgee": "Sancho Panza",
    "Samwise": "Sancho Panza",
    "Gimli": "Dorotea",
    "Boromir": "Dulcinea del Toboso",
    "Mordor": "Sierra Morena",
    "Rivendell": "La Mancha",
    "The Shire": "El Toboso",
    "Minas Tirith": "Barcelona",
    "Isengard": "La Venta",
    "Lord of the Rings": "Don Quijote de la Mancha",
    "The Lord of the Rings": "Don Quijote de la Mancha",
    "LOTR": "Don Quijote",
    "Middle-earth": "La Mancha",
    "Middle Earth": "La Mancha",
}

SW_TO_ODISEA = {
    "luke_skywalker": "odiseo",
    "darth_vader": "poseidon",
    "leia_organa": "penelope",
    "han_solo": "telemachus",
    "yoda": "athena",
    "obi_wan": "circe",
    "obi_wan_kenobi": "circe",
    "palpatine": "polyphemus",
    "emperor_palpatine": "polyphemus",
    "chewbacca": "calypso",
    "tatooine": "ithaca",
    "coruscant": "troy",
    "death_star": "olympus",
    "hoth": "isle_of_circe",
    "endor": "underworld",
}

SW_LABEL_MAP = {
    "Luke Skywalker": "Odiseo",
    "Darth Vader": "Poseidón",
    "Leia Organa": "Penélope",
    "Han Solo": "Telémaco",
    "Yoda": "Atenea",
    "Obi-Wan Kenobi": "Circe",
    "Obi-Wan": "Circe",
    "Emperor Palpatine": "Polifemo",
    "Palpatine": "Polifemo",
    "Chewbacca": "Calipso",
    "Tatooine": "Ítaca",
    "Coruscant": "Troya",
    "Death Star": "Olimpo",
    "Hoth": "Isla de Circe",
    "Endor": "Inframundo",
    "Star Wars": "La Odisea",
    "Jedi": "héroe griego",
    "Sith": "titán",
    "the Force": "la astucia divina",
    "lightsaber": "arco legendario",
}

DUNE_TO_GOTHIC = {
    "paul_atreides": "victor_frankenstein",
    "leto_atreides": "henry_clerval",
    "duke_leto_atreides": "henry_clerval",
    "jessica": "elizabeth_lavenza",
    "lady_jessica": "elizabeth_lavenza",
    "baron_harkonnen": "count_dracula",
    "stilgar": "jonathan_harker",
    "chani": "mina_harker",
    "duncan_idaho": "the_creature",
    "arrakis": "ingolstadt",
    "caladan": "geneva",
    "giedi_prime": "castle_dracula",
}

DUNE_LABEL_MAP = {
    "Paul Atreides": "Victor Frankenstein",
    "Duke Leto Atreides": "Henry Clerval",
    "Duke Leto": "Henry Clerval",
    "Leto Atreides": "Henry Clerval",
    "Lady Jessica": "Elizabeth Lavenza",
    "Jessica": "Elizabeth Lavenza",
    "Baron Harkonnen": "Count Dracula",
    "Stilgar": "Jonathan Harker",
    "Chani": "Mina Harker",
    "Duncan Idaho": "The Creature",
    "Arrakis": "Ingolstadt",
    "Caladan": "Geneva",
    "Giedi Prime": "Castle Dracula",
    "Dune": "Frankenstein",
    "Fremen": "villagers",
    "spice": "the elixir",
    "sandworm": "the creature",
    "Kwisatz Haderach": "the reanimated being",
    "Bene Gesserit": "the alchemists",
}

# Detect which universe an example belongs to
HP_DETECT = {"harry_potter", "hermione", "hogwarts", "dumbledore", "snape",
             "voldemort", "hagrid", "draco_malfoy", "sirius_black", "mcgonagall",
             "diagon_alley", "privet_drive", "hogsmeade", "forbidden_forest",
             "ministry_of_magic", "ron_weasley", "granger"}

LOTR_DETECT = {"frodo", "gandalf", "aragorn", "legolas", "sauron", "gollum",
               "samwise", "mordor", "rivendell", "the_shire", "minas_tirith",
               "isengard", "gimli", "boromir", "lord of the rings", "middle-earth",
               "middle earth", "hobbit"}

SW_DETECT = {"luke_skywalker", "darth_vader", "leia_organa", "han_solo",
             "yoda", "obi_wan", "palpatine", "chewbacca", "tatooine",
             "coruscant", "death_star", "hoth", "endor", "star wars",
             "jedi", "sith", "lightsaber"}

DUNE_DETECT = {"paul_atreides", "leto_atreides", "jessica", "baron_harkonnen",
               "stilgar", "chani", "duncan_idaho", "arrakis", "caladan",
               "giedi_prime", "dune", "fremen", "spice", "sandworm",
               "kwisatz", "bene_gesserit"}


def detect_universe(text: str) -> str | None:
    """Detect which copyrighted universe an example uses."""
    text_lower = text.lower()
    for term in HP_DETECT:
        if term in text_lower:
            return "hp"
    for term in LOTR_DETECT:
        if term in text_lower:
            return "lotr"
    for term in SW_DETECT:
        if term in text_lower:
            return "sw"
    for term in DUNE_DETECT:
        if term in text_lower:
            return "dune"
    return None


def replace_in_text(text: str, universe: str) -> str:
    """Replace copyrighted names/terms in free text with public domain equivalents."""
    if universe == "hp":
        label_map = HP_LABEL_MAP
    elif universe == "lotr":
        label_map = LOTR_LABEL_MAP
    elif universe == "sw":
        label_map = SW_LABEL_MAP
    elif universe == "dune":
        label_map = DUNE_LABEL_MAP
    else:
        return text

    # Sort by length descending to replace longer strings first
    for old, new in sorted(label_map.items(), key=lambda x: -len(x[0])):
        text = text.replace(old, new)
        # Also handle lowercase versions in running text
        if old[0].isupper() and old.lower() != old:
            text = text.replace(old.lower(), new.lower())

    return text


def replace_in_json_obj(obj, universe: str):
    """Recursively replace copyrighted IDs and labels in a JSON object."""
    if universe == "hp":
        id_map = HP_TO_SHERLOCK
        label_map = HP_LABEL_MAP
    elif universe == "lotr":
        id_map = LOTR_TO_QUIJOTE
        label_map = LOTR_LABEL_MAP
    elif universe == "sw":
        id_map = SW_TO_ODISEA
        label_map = SW_LABEL_MAP
    elif universe == "dune":
        id_map = DUNE_TO_GOTHIC
        label_map = DUNE_LABEL_MAP
    else:
        return obj

    if isinstance(obj, str):
        # Replace labels in string values
        result = obj
        for old, new in sorted(label_map.items(), key=lambda x: -len(x[0])):
            result = result.replace(old, new)
        return result
    elif isinstance(obj, list):
        return [replace_in_json_obj(item, universe) for item in obj]
    elif isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            if key in ("id", "source", "target", "entity", "existing_id"):
                # Replace entity IDs
                if isinstance(value, str) and value in id_map:
                    new_dict[key] = id_map[value]
                elif isinstance(value, str):
                    # Try partial match for compound IDs
                    new_val = value
                    for old_id, new_id in sorted(id_map.items(), key=lambda x: -len(x[0])):
                        new_val = new_val.replace(old_id, new_id)
                    new_dict[key] = new_val
                else:
                    new_dict[key] = value
            elif key == "label":
                new_dict[key] = replace_in_text(str(value), universe) if isinstance(value, str) else value
            elif key == "text":
                new_dict[key] = replace_in_text(str(value), universe) if isinstance(value, str) else value
            else:
                new_dict[key] = replace_in_json_obj(value, universe)
        return new_dict
    else:
        return obj


def clean_example(example: dict) -> dict:
    """Clean a single training example: replace IP + update system prompt."""
    messages = example["messages"]

    # 1. Update system prompt
    messages[0]["content"] = S1_SYSTEM_PROMPT

    # 2. Detect copyrighted universe
    full_text = json.dumps(example, ensure_ascii=False)
    universe = detect_universe(full_text)

    if universe is None:
        return example

    # 3. Replace in user message (free text)
    messages[1]["content"] = replace_in_text(messages[1]["content"], universe)

    # 4. Replace in assistant output (structured JSON)
    try:
        assistant_obj = json.loads(messages[2]["content"])
        assistant_obj = replace_in_json_obj(assistant_obj, universe)

        # Also replace in topic label if present
        if "topic" in assistant_obj and assistant_obj["topic"].get("label"):
            assistant_obj["topic"]["label"] = replace_in_text(
                assistant_obj["topic"]["label"], universe
            )

        messages[2]["content"] = json.dumps(assistant_obj, ensure_ascii=False)
    except (json.JSONDecodeError, KeyError, IndexError):
        # If we can't parse, do text-level replacement
        messages[2]["content"] = replace_in_text(messages[2]["content"], universe)

    return example


def process_file(input_path: Path, output_path: Path) -> dict:
    """Process a JSONL file: clean IP + update prompt. Returns stats."""
    examples = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    stats = Counter()
    stats["total"] = len(examples)

    cleaned = []
    for ex in examples:
        full_text = json.dumps(ex, ensure_ascii=False)
        universe = detect_universe(full_text)
        if universe:
            stats[f"replaced_{universe}"] += 1
            stats["replaced_total"] += 1
        else:
            stats["clean"] += 1

        cleaned.append(clean_example(ex))

    # Validate all cleaned examples
    valid = 0
    errors = []
    for i, ex in enumerate(cleaned):
        try:
            assistant_content = ex["messages"][2]["content"]
            ok, result = validate_s1(assistant_content)
            if ok:
                valid += 1
            else:
                errors.append((i + 1, str(result)))
        except Exception as e:
            errors.append((i + 1, str(e)))
    stats["schema_valid"] = valid
    stats["schema_errors"] = len(errors)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in cleaned:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    return dict(stats), errors[:5]


def main():
    base = Path(__file__).parent.parent

    files_to_process = [
        # v2 full training
        (
            base / "training_data" / "v2" / "s1_v2_full_training.jsonl",
            base / "training_data" / "v3_new" / "v2_cleaned_training.jsonl",
        ),
        # v2 full validation
        (
            base / "training_data" / "v2" / "s1_v2_full_validation.jsonl",
            base / "training_data" / "v3_new" / "v2_cleaned_validation.jsonl",
        ),
        # v3 groups
        (
            base / "training_data" / "v3" / "v3_g1_s1_intent.jsonl",
            base / "training_data" / "v3_new" / "v3_g1_cleaned.jsonl",
        ),
        (
            base / "training_data" / "v3" / "v3_g2_s15_recall.jsonl",
            base / "training_data" / "v3_new" / "v3_g2_cleaned.jsonl",
        ),
        (
            base / "training_data" / "v3" / "v3_g3_curate_multientity.jsonl",
            base / "training_data" / "v3_new" / "v3_g3_cleaned.jsonl",
        ),
        (
            base / "training_data" / "v3" / "v3_g4_gaps.jsonl",
            base / "training_data" / "v3_new" / "v3_g4_cleaned.jsonl",
        ),
    ]

    print("=" * 60)
    print("CLEAN AND UPDATE TRAINING DATA FOR V3")
    print("=" * 60)

    total_replaced = 0
    total_examples = 0

    for input_path, output_path in files_to_process:
        if not input_path.exists():
            print(f"\nSKIPPED (not found): {input_path.name}")
            continue

        print(f"\n--- {input_path.name} ---")
        stats, errors = process_file(input_path, output_path)

        total_examples += stats["total"]
        total_replaced += stats.get("replaced_total", 0)

        print(f"  Total: {stats['total']}")
        print(f"  Clean (no IP): {stats.get('clean', 0)}")
        print(f"  Replaced: {stats.get('replaced_total', 0)}")
        if stats.get("replaced_hp"):
            print(f"    HP->Sherlock: {stats['replaced_hp']}")
        if stats.get("replaced_lotr"):
            print(f"    LOTR->Quijote: {stats['replaced_lotr']}")
        if stats.get("replaced_sw"):
            print(f"    SW->Odisea: {stats['replaced_sw']}")
        if stats.get("replaced_dune"):
            print(f"    Dune->Gothic: {stats['replaced_dune']}")
        print(f"  Schema valid: {stats['schema_valid']}/{stats['total']}")
        if errors:
            print(f"  First errors:")
            for line_num, err in errors:
                print(f"    Line {line_num}: {err[:100]}")
        print(f"  Output: {output_path}")

    print(f"\n{'=' * 60}")
    print(f"TOTAL: {total_examples} examples, {total_replaced} IP replaced")
    print(f"System prompt updated in ALL examples")
    print(f"Output directory: training_data/v3_new/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

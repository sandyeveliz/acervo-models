#!/usr/bin/env python3
"""
Generate V4 training data for Acervo S1 model.

Produces ~600 examples across 7 skill groups:
  G1. JSON discipline + existing_id (150)
  G2. Numeric facts (120)
  G3. Empty output (90)
  G4. Relations (90)
  G5. Topic changes (60)
  G6. Dedup & corrections (60)
  G7. Multi-entity complex (30)

Schema V4: nested intent, description on entities, entity_id in facts.
SFT from base Qwen3.5-9B — no legacy data reuse.

Usage:
    cd 01_dataset
    python generate_s1_v4_training.py [--seed 42]
"""

import json
import random
import argparse
from pathlib import Path

# --- Import pools from v1 generator ---
from generate_s1_training import (
    PERSONS, PROJECTS, ORGS, FRONTEND, BACKEND, DATABASES, CLOUD, INFRA,
    CSS_FW, LANGUAGES, APP_TYPES_EN, APP_TYPES_ES, JOB_TITLES,
    _id, pick, pick_n, pick_hint, format_user_input,
)

# --- Import Argentine pools from v3_new generator ---
from generate_s1_v3_new_training import (
    AR_PERSONS, AR_CITIES, AR_BARRIOS, AR_BUSINESSES,
    FIN_INSTRUMENTS, MEDICAL, TRAVEL_DESTINATIONS, TRAVEL_BARRIOS,
    TRAVEL_ATTRACTIONS, FITNESS_ACTIVITIES, TECH_ES, PROJECTS_ES,
)

from schema_v4 import (
    S1_V4_SYSTEM_PROMPT, validate_s1_v4, validate_cross_references,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "training_data" / "v4"

# ═══════════════════════════════════════════════════════════════════════════
# V4 Helper Functions
# ═══════════════════════════════════════════════════════════════════════════

def ent(nid, label, ntype, layer, description, existing_id=None):
    """Build a V4 entity dict for the output."""
    return {
        "id": nid, "label": label, "type": ntype, "layer": layer,
        "description": description, "existing_id": existing_id,
    }

def fact(entity_id, text, speaker="user"):
    """Build a V4 fact dict with entity_id key."""
    return {"entity_id": entity_id, "text": text, "speaker": speaker}

def r(source, target, relation):
    """Build a relation dict."""
    return {"source": source, "target": target, "relation": relation}

def out(intent_type, retrieval, action="same", label="", entities=None,
        relations=None, facts=None):
    """Build a complete V4 output dict."""
    return {
        "topic": {"action": action, "label": label},
        "intent": {"type": intent_type, "retrieval": retrieval},
        "entities": entities or [],
        "relations": relations or [],
        "facts": facts or [],
    }

def enode(nid, label, ntype, facts_list=None):
    """Build an EXISTING NODE for the user message (V4 format).

    Type is Title Case, facts are plain strings.
    """
    n = {"id": nid, "label": label, "type": ntype.title()}
    if facts_list:
        n["facts"] = facts_list
    return n

def example(existing_nodes, topic_hint, current_topic, prev_assistant,
            user_msg, output):
    """Build a complete V4 training example."""
    nodes_json = json.dumps(existing_nodes, ensure_ascii=False) if existing_nodes else "[]"
    topic_str = current_topic if current_topic else "null"
    prev_str = prev_assistant if prev_assistant else "null"
    user_content = (
        f"EXISTING NODES:\n{nodes_json}\n\n"
        f"TOPIC HINT: {topic_hint}\n"
        f"CURRENT TOPIC: {topic_str}\n\n"
        f"PREVIOUS ASSISTANT: {prev_str}\n"
        f"USER: {user_msg}"
    )
    return {
        "messages": [
            {"role": "system", "content": S1_V4_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": json.dumps(output, ensure_ascii=False)},
        ]
    }

def _amount_ars():
    """Random ARS amount string."""
    n = random.choice([150_000, 250_000, 500_000, 800_000, 1_200_000,
                       2_500_000, 3_800_000, 4_200_000, 5_500_000, 8_000_000])
    return f"{n:,.0f}".replace(",", ".")

def _amount_usd():
    """Random USD amount string."""
    return str(random.choice([1_500, 3_000, 5_000, 8_000, 12_000, 18_000,
                              25_000, 35_000, 50_000, 80_000, 120_000, 180_000]))

def _pct():
    """Random percentage string."""
    return str(random.choice([5, 8, 10, 12, 15, 18, 20, 25, 30, 35, 45, 60, 75, 80, 90]))

def _months():
    """Random month count."""
    return str(random.choice([2, 3, 4, 6, 8, 10, 12, 18, 24]))

def _prev_es():
    """Random Spanish previous assistant response."""
    return pick([
        "Entendido, queda registrado.",
        "Dale, lo anoto.",
        "Perfecto, guardado.",
        "Ok, tomé nota.",
        "Listo, lo tengo.",
        "Anotado. ¿Algo más?",
    ])

def _prev_en():
    """Random English previous assistant response."""
    return pick([
        "Got it, noted.",
        "Understood.",
        "Noted. Anything else?",
        "Recorded.",
        "Got it.",
        "All right, stored.",
    ])


# ═══════════════════════════════════════════════════════════════════════════
# Graph State Generators (V4 format — enode with Title Case types, string facts)
# ═══════════════════════════════════════════════════════════════════════════

def software_graph_v4():
    """Software project graph with V4 existing nodes."""
    proj = pick(PROJECTS)
    org = pick(ORGS)
    fe = pick(FRONTEND)
    be = pick(BACKEND)
    db = pick(DATABASES)
    people = pick_n(PERSONS, random.randint(1, 3))
    app = pick(APP_TYPES_EN)
    nodes = [
        enode(proj[0], proj[1], "project", [f"Internal {app} at {org[1]}", f"{fe[1]} + {be[1]} stack"]),
        enode(org[0], org[1], "organization"),
        enode(fe[0], fe[1], "technology"),
        enode(be[0], be[1], "technology"),
        enode(db[0], db[1], "technology"),
    ]
    for p in people:
        nodes.append(enode(p[0], p[1], "person"))
    return nodes, proj, org, fe, be, db, people


def personal_finance_graph_v4():
    """Personal finance graph (Argentine)."""
    person = pick(AR_PERSONS)
    city = pick(AR_CITIES)
    funds = pick_n(FIN_INSTRUMENTS[:6], random.randint(2, 3))
    nodes = [
        enode(person[0], person[1], "person", [f"Vive en {city[1]}"]),
        enode(city[0], city[1], "place"),
    ]
    for f_ in funds:
        nodes.append(enode(f_[0], f_[1], "concept", [pick([
            "Renta variable, riesgo medio", "Renta fija, bajo riesgo",
            "Objetivo: vacaciones", "Objetivo: jubilación",
            "Ahorro mensual", "Inversión a largo plazo",
        ])]))
    return nodes, person, city, funds


def real_estate_graph_v4():
    """Real estate / construction graph (Argentine)."""
    person = pick(AR_PERSONS)
    city = pick(AR_CITIES)
    barrio = pick(AR_BARRIOS)
    architect = pick([p for p in AR_PERSONS if p != person])
    builder = pick(AR_BUSINESSES[:6])
    lot_id = f"terreno_{barrio[0]}"
    nodes = [
        enode(person[0], person[1], "person"),
        enode(city[0], city[1], "place"),
        enode(barrio[0], barrio[1], "place"),
        enode(lot_id, f"Terreno en {barrio[1]}", "place",
              [f"Zona residencial en {city[1]}"]),
        enode(architect[0], architect[1], "person", ["Arquitecto"]),
        enode(builder[0], builder[1], "organization"),
    ]
    return nodes, person, city, barrio, architect, builder, lot_id


def health_family_graph_v4():
    """Health / family graph (Argentine)."""
    parent = pick(AR_PERSONS)
    partner = pick([p for p in AR_PERSONS if p != parent])
    child_name = pick(["Emilia", "Bautista", "Olivia", "Lautaro", "Emma", "Thiago"])
    child_id = _id(child_name)
    city = pick(AR_CITIES)
    clinic_name = pick(["Clínica San Lucas", "Clínica del Valle", "Sanatorio Central",
                        "Hospital Privado", "Centro Médico Sur"])
    clinic_id = _id(clinic_name)
    nodes = [
        enode(parent[0], parent[1], "person"),
        enode(partner[0], partner[1], "person"),
        enode(child_id, child_name, "person", [f"Hijo/a de {parent[1]}"]),
        enode(city[0], city[1], "place"),
        enode(clinic_id, clinic_name, "organization", [f"En {city[1]}"]),
    ]
    return nodes, parent, partner, (child_id, child_name), city, (clinic_id, clinic_name)


def travel_graph_v4():
    """Travel planning graph."""
    person = pick(AR_PERSONS)
    dest = pick(TRAVEL_DESTINATIONS)
    city_origin = pick(AR_CITIES)
    trip_id = f"viaje_{dest[0]}"
    barrio = pick(TRAVEL_BARRIOS)
    nodes = [
        enode(person[0], person[1], "person", [f"Vive en {city_origin[1]}"]),
        enode(city_origin[0], city_origin[1], "place"),
        enode(dest[0], dest[1], "place"),
        enode(trip_id, f"Viaje a {dest[1]}", "event", ["Vacaciones planificadas"]),
    ]
    return nodes, person, city_origin, dest, trip_id, barrio


def freelance_graph_v4():
    """Work / freelance graph (Argentine)."""
    person = pick(AR_PERSONS)
    project = pick(PROJECTS_ES)
    client = pick(AR_BUSINESSES)
    city = pick(AR_CITIES)
    tech = pick_n(TECH_ES, random.randint(2, 3))
    nodes = [
        enode(person[0], person[1], "person", [f"Freelancer en {city[1]}"]),
        enode(project[0], project[1], "project", [f"Cliente: {client[1]}"]),
        enode(client[0], client[1], "organization"),
        enode(city[0], city[1], "place"),
    ]
    for t in tech:
        nodes.append(enode(t[0], t[1], "technology"))
    return nodes, person, project, client, city, tech


def literature_graph_v4():
    """Literature graph — public domain only."""
    universes = {
        "sherlock": {
            "chars": [("sherlock_holmes", "Sherlock Holmes"), ("dr_watson", "Dr. Watson"),
                      ("moriarty", "Professor Moriarty"), ("mrs_hudson", "Mrs. Hudson"),
                      ("irene_adler", "Irene Adler"), ("lestrade", "Inspector Lestrade")],
            "places": [("baker_street", "221B Baker Street"), ("london", "London"),
                       ("reichenbach", "Reichenbach Falls")],
            "title": "Sherlock Holmes",
        },
        "quijote": {
            "chars": [("don_quijote", "Don Quijote"), ("sancho_panza", "Sancho Panza"),
                      ("dulcinea", "Dulcinea del Toboso"), ("rocinante", "Rocinante"),
                      ("cura", "El Cura"), ("barbero", "El Barbero")],
            "places": [("la_mancha", "La Mancha"), ("el_toboso", "El Toboso"),
                       ("barcelona_quijote", "Barcelona")],
            "title": "Don Quijote de la Mancha",
        },
        "odyssey": {
            "chars": [("odysseus", "Odysseus"), ("penelope", "Penelope"),
                      ("telemachus", "Telemachus"), ("athena", "Athena"),
                      ("cyclops", "Polyphemus"), ("circe", "Circe")],
            "places": [("ithaca", "Ithaca"), ("troy", "Troy"),
                       ("mount_olympus", "Mount Olympus")],
            "title": "The Odyssey",
        },
        "gothic": {
            "chars": [("dracula", "Count Dracula"), ("van_helsing", "Van Helsing"),
                      ("frankenstein", "Victor Frankenstein"), ("creature", "The Creature"),
                      ("mina_harker", "Mina Harker"), ("jonathan_harker", "Jonathan Harker")],
            "places": [("transylvania", "Transylvania"), ("castle_dracula", "Castle Dracula"),
                       ("ingolstadt", "Ingolstadt")],
            "title": "Gothic Literature",
        },
    }
    key = pick(list(universes.keys()))
    u = universes[key]
    chars = pick_n(u["chars"], random.randint(2, 4))
    places = pick_n(u["places"], random.randint(1, 2))
    nodes = []
    for c in chars:
        nodes.append(enode(c[0], c[1], "person"))
    for p in places:
        nodes.append(enode(p[0], p[1], "place"))
    return nodes, chars, places, u["title"], key


# ═══════════════════════════════════════════════════════════════════════════
# G1. JSON Discipline + existing_id  (150 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g1_existing_id_software():
    """existing_id correct — user refers to existing node, model uses existing_id."""
    examples = []
    messages_en = [
        ("I want to add Redis caching to {proj}", "uses_technology",
         "redis", "Redis", "technology", "UNIVERSAL", "In-memory data store for caching"),
        ("Let's switch the deployment to AWS", "deployed_on",
         "aws", "AWS", "technology", "UNIVERSAL", "Amazon Web Services cloud platform"),
        ("We need to add monitoring with Datadog", "uses_technology",
         "datadog", "Datadog", "technology", "UNIVERSAL", "Cloud monitoring and analytics platform"),
        ("The frontend should use Tailwind for styling", "uses_technology",
         "tailwind", "Tailwind CSS", "technology", "UNIVERSAL", "Utility-first CSS framework"),
        ("{person} is now the tech lead for {proj}", "maintains", None, None, None, None, None),
        ("We're migrating {proj} from {fe} to Svelte", "uses_technology",
         "svelte", "Svelte", "technology", "UNIVERSAL", "Reactive frontend compiler"),
    ]
    for _ in range(20):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        tpl = pick(messages_en)
        person = pick(people) if people else pick(PERSONS)
        msg = tpl[0].format(proj=proj[1], person=person[1], fe=fe[1])
        topic = proj[1].lower()

        if tpl[2] is not None:
            entities = [ent(tpl[2], tpl[3], tpl[4], tpl[5], tpl[6])]
            relations = [r(proj[0], tpl[2], tpl[1])]
            facts = []
        else:
            entities = []
            relations = [r(person[0], proj[0], tpl[1])]
            facts = [fact(proj[0], f"Tech lead: {person[1]}", "user")]

        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), msg,
            out("specific", "summary_only", "same", topic,
                entities, relations, facts)
        ))

    # Spanish — construction existing_id
    messages_es = [
        "El terreno tiene salida a dos calles y buena orientación norte",
        "Nos confirmaron que el terreno tiene gas natural y cloacas",
        "La escritura del terreno está en orden, sin deuda municipal",
        "El terreno tiene 12 metros de frente y 30 de fondo",
        "Ya firmamos el boleto de compraventa del terreno",
    ]
    for _ in range(10):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        msg = pick(messages_es)
        fact_text = msg.replace("El terreno tiene ", "").replace("el terreno", "").strip()
        if len(fact_text) > 80:
            fact_text = fact_text[:77] + "..."
        examples.append(example(
            nodes, pick_hint("same", "compra terreno"), "compra terreno",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "compra terreno",
                facts=[fact(lot_id, fact_text, "user")])
        ))

    # Spanish — finance existing_id (facts on existing funds)
    finance_msgs = [
        ("Metí {amt} ARS en el {fund}", "{fund}: inversión de {amt} ARS"),
        ("El {fund} me dio {pct}% este mes", "{fund}: rendimiento {pct}% mensual"),
        ("Voy a rescatar del {fund} para pagar el alquiler", "{fund}: rescate parcial para alquiler"),
        ("Pasé {amt} ARS del {fund_a} al {fund_b}", "Transferencia: {amt} ARS de {fund_a} a {fund_b}"),
    ]
    for _ in range(10):
        nodes, person, city, funds = personal_finance_graph_v4()
        fund = pick(funds)
        tpl = pick(finance_msgs)
        amt = _amount_ars()
        pct = _pct()
        fund_b = pick([f for f in funds if f != fund]) if len(funds) > 1 else fund
        msg = tpl[0].format(amt=amt, fund=fund[1], pct=pct,
                            fund_a=fund[1], fund_b=fund_b[1])
        fact_text = tpl[1].format(amt=amt, fund=fund[1], pct=pct,
                                  fund_a=fund[1], fund_b=fund_b[1])
        facts_list = [fact(fund[0], fact_text, "user")]
        if "fund_b" in tpl[0] and fund_b != fund:
            facts_list.append(fact(fund_b[0], f"Recibe {amt} ARS desde {fund[1]}", "user"))
        examples.append(example(
            nodes, pick_hint("same", "finanzas personales"), "finanzas personales",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "finanzas personales",
                facts=facts_list)
        ))
    return examples


def gen_g1_facts_toplevel():
    """All facts go to top-level facts[] with valid entity_id."""
    examples = []

    # English — new entity + facts on existing
    for _ in range(20):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        new_person = pick([p for p in PERSONS if p not in people])
        job = pick(JOB_TITLES)
        topic = proj[1].lower()
        salary = pick(["95k", "110k", "130k", "150k", "180k"])
        msg = f"We hired {new_person[1]} as the new {job} for {proj[1]}. Salary is {salary}/year."
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), msg,
            out("specific", "summary_only", "same", topic,
                entities=[ent(new_person[0], new_person[1], "person", "PERSONAL",
                              f"New {job} for {proj[1]}")],
                relations=[r(new_person[0], proj[0], "maintains")],
                facts=[
                    fact(new_person[0], f"Salary: {salary} USD/year", "user"),
                    fact(proj[0], f"New {job}: {new_person[1]}", "user"),
                ])
        ))

    # Spanish — facts on existing entities
    for _ in range(20):
        nodes, person, city, funds = personal_finance_graph_v4()
        amt = _amount_ars()
        pct = _pct()
        cat = pick(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"])
        msg = f"Mi sueldo bruto es {amt} ARS/mes, monotributista categoría {cat}. Ahorro {pct}% mensual."
        examples.append(example(
            nodes, pick_hint("same", "finanzas personales"), "finanzas personales",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "finanzas personales",
                facts=[
                    fact(person[0], f"Sueldo bruto: {amt} ARS/mes", "user"),
                    fact(person[0], f"Monotributista categoría {cat}", "user"),
                    fact(person[0], f"Tasa de ahorro: {pct}% mensual", "user"),
                ])
        ))
    return examples


def gen_g1_create_entity_for_fact():
    """When a fact has no entity, create one first."""
    examples = []

    # English — user mentions a new thing that needs an entity
    for _ in range(15):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        scenarios = [
            (f"Our new CI pipeline takes 12 minutes to complete and costs $0.08 per run",
             "ci_pipeline", "CI Pipeline", "technology", "PERSONAL",
             f"Continuous integration pipeline for {proj[1]}",
             [fact("ci_pipeline", "Build time: 12 minutes", "user"),
              fact("ci_pipeline", "Cost: $0.08 per run", "user")]),
            (f"The staging environment is running on a t3.medium with 4GB RAM",
             "staging_env", "Staging Environment", "technology", "PERSONAL",
             f"Staging environment for {proj[1]}",
             [fact("staging_env", "Instance: t3.medium, 4GB RAM", "user")]),
            (f"We have a Grafana dashboard tracking p99 latency at 230ms",
             "grafana_dashboard", "Grafana Dashboard", "technology", "PERSONAL",
             f"Monitoring dashboard for {proj[1]}",
             [fact("grafana_dashboard", "p99 latency: 230ms", "user")]),
            (f"Our Sentry error tracking caught 47 unhandled exceptions last week",
             "sentry", "Sentry", "technology", "UNIVERSAL",
             "Error tracking and performance monitoring",
             [fact("sentry", "47 unhandled exceptions last week", "user")]),
        ]
        s = pick(scenarios)
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), s[0],
            out("specific", "summary_only", "same", topic,
                entities=[ent(s[1], s[2], s[3], s[4], s[5])],
                facts=s[6])
        ))

    # Spanish — construction: new entity for fact
    for _ in range(15):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        scenarios = [
            (f"El electricista Jorge Muñoz nos cobra {_amount_usd()} USD por toda la instalación",
             "jorge_munoz", "Jorge Muñoz", "person", "PERSONAL", "Electricista para la obra",
             [fact("jorge_munoz", f"Presupuesto instalación eléctrica: {_amount_usd()} USD", "user")]),
            (f"Vamos a poner pisos de porcelanato Cerro Negro, 45x45, a {_amount_ars()} ARS/m2",
             "porcelanato", "Porcelanato Cerro Negro", "concept", "PERSONAL", "Material de piso para la obra",
             [fact("porcelanato", f"Formato: 45x45, precio: {_amount_ars()} ARS/m2", "user")]),
            (f"La inmobiliaria Lagos nos gestionó el crédito hipotecario con tasa del {_pct()}%",
             None, None, None, None, None, None),  # entity already in EXISTING NODES
        ]
        s = pick(scenarios[:2])  # use first 2 which create entities
        examples.append(example(
            nodes, pick_hint("same", "obra"), "obra", _prev_es(), s[0],
            out("specific", "summary_only", "same", "obra",
                entities=[ent(s[1], s[2], s[3], s[4], s[5])],
                facts=s[6])
        ))
    return examples


def gen_g1_json_strict():
    """Ambiguous/confusing input — always return valid JSON."""
    examples = []

    empty_msgs_es = [
        "mmm no sé, estaba pensando en algo pero se me fue",
        "ajá",
        "bueno, después vemos",
        "ni idea la verdad",
        "puede ser, no me acuerdo bien",
        "yyy... no, nada, dejá",
        "jajaja",
        "dale dale",
        "no me hagas caso",
        "esperá que pienso...",
    ]
    empty_msgs_en = [
        "hmm let me think about that",
        "yeah maybe",
        "not sure actually",
        "I guess so",
        "lol ok",
        "never mind",
        "hold on",
        "meh",
        "whatever works I guess",
        "I'll figure it out later",
    ]

    for msg in empty_msgs_es:
        nodes = [enode("general", "General", "concept")] if random.random() > 0.5 else []
        topic = "general" if nodes else ""
        examples.append(example(
            nodes, pick_hint("query", topic), topic or "null", _prev_es(), msg,
            out("chat", "summary_only", "same", topic)
        ))

    for msg in empty_msgs_en:
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        examples.append(example(
            nodes, pick_hint("query", topic), topic, _prev_en(), msg,
            out("chat", "summary_only", "same", topic)
        ))
    return examples


def gen_g1_traps():
    """Traps — similar name to existing entity, but DON'T use existing_id."""
    examples = []

    # English — "Redis" exists but user talks about "Redis Cluster" (new entity)
    for _ in range(10):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        # Add redis to existing nodes
        nodes.append(enode("redis", "Redis", "technology", ["In-memory cache"]))
        scenarios = [
            (f"We're evaluating Redis Cluster for the {proj[1]} session store",
             "redis_cluster", "Redis Cluster", "technology", "UNIVERSAL",
             "Distributed Redis deployment mode", None),
            (f"The new React Native mobile app will complement {proj[1]}",
             "react_native_app", "React Native App", "project", "PERSONAL",
             f"Mobile companion for {proj[1]}", None),
        ]
        s = pick(scenarios)
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), s[0],
            out("specific", "summary_only", "same", topic,
                entities=[ent(s[1], s[2], s[3], s[4], s[5])],
                relations=[r(proj[0], s[1], "uses_technology" if s[3] == "technology" else "part_of")])
        ))

    # Spanish — "Fondo Conservador" exists but user mentions "Fondo Conservador Plus" (new)
    for _ in range(10):
        nodes, person, city, funds = personal_finance_graph_v4()
        fund = pick(funds)
        new_name = fund[1] + " Plus"
        new_id = _id(new_name)
        msg = f"Vi que sacaron un {new_name} con mejor tasa, lo estoy evaluando"
        examples.append(example(
            nodes, pick_hint("same", "inversiones"), "inversiones",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "inversiones",
                entities=[ent(new_id, new_name, "concept", "PERSONAL",
                              f"Variante mejorada de {fund[1]}")],
                facts=[fact(new_id, "En evaluación, mejor tasa que versión original", "user")])
        ))
    return examples


def gen_g1_all():
    """Generate all G1 examples (~150)."""
    all_ex = []
    all_ex += gen_g1_existing_id_software()     # ~40
    all_ex += gen_g1_facts_toplevel()            # ~40
    all_ex += gen_g1_create_entity_for_fact()    # ~30
    all_ex += gen_g1_json_strict()               # ~20
    all_ex += gen_g1_traps()                     # ~20
    return all_ex


# ═══════════════════════════════════════════════════════════════════════════
# G2. Numeric Facts  (120 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g2_finance():
    """Numeric facts — personal finance."""
    examples = []
    templates = [
        ("Mi sueldo neto es {amt} ARS/mes", "Sueldo neto: {amt} ARS/mes"),
        ("El alquiler me sale {amt} ARS por mes", "Alquiler: {amt} ARS/mes"),
        ("Gasté {amt} ARS en el súper esta semana", "Gasto supermercado semanal: {amt} ARS"),
        ("Tengo {usd} USD ahorrados en el banco", "Ahorro en banco: {usd} USD"),
        ("La cuota del auto es {amt} ARS por mes", "Cuota auto: {amt} ARS/mes"),
        ("Me depositaron {amt} ARS de aguinaldo", "Aguinaldo: {amt} ARS"),
        ("El seguro de salud cuesta {amt} ARS/mes", "Seguro salud: {amt} ARS/mes"),
        ("Invertí {usd} USD en CEDEARs", "Inversión CEDEARs: {usd} USD"),
        ("El dólar MEP está a {price} ARS", "Dólar MEP: {price} ARS"),
        ("Mi tarjeta tiene un saldo de {amt} ARS", "Saldo tarjeta: {amt} ARS"),
    ]
    for _ in range(30):
        nodes, person, city, funds = personal_finance_graph_v4()
        tpl = pick(templates)
        amt = _amount_ars()
        usd = _amount_usd()
        price = str(random.randint(900, 1500))
        msg = tpl[0].format(amt=amt, usd=usd, price=price)
        fact_text = tpl[1].format(amt=amt, usd=usd, price=price)
        examples.append(example(
            nodes, pick_hint("same", "finanzas personales"), "finanzas personales",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "finanzas personales",
                facts=[fact(person[0], fact_text, "user")])
        ))
    return examples


def gen_g2_construction():
    """Numeric facts — construction/real estate."""
    examples = []
    templates = [
        ("El presupuesto de obra llave en mano es {usd} USD",
         "Presupuesto llave en mano: {usd} USD"),
        ("El terreno tiene {m2}m2 a {price} USD/m2",
         "Superficie: {m2}m2, precio: {price} USD/m2"),
        ("Las aberturas de aluminio salen {usd} USD en total",
         "Aberturas aluminio: {usd} USD"),
        ("La losa nos cotizaron {amt} ARS con materiales incluidos",
         "Losa con materiales: {amt} ARS"),
        ("El pozo de agua costó {amt} ARS, 40 metros de profundidad",
         "Pozo de agua: {amt} ARS, 40m profundidad"),
        ("La obra va por el {pct}% de avance, llevamos {months} meses",
         "Avance obra: {pct}%, {months} meses transcurridos"),
    ]
    for _ in range(18):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        tpl = pick(templates)
        amt = _amount_ars()
        usd = _amount_usd()
        m2 = str(random.choice([200, 300, 400, 500, 600, 800, 1000]))
        price = str(random.choice([50, 70, 85, 100, 120, 150]))
        pct = _pct()
        months = _months()
        msg = tpl[0].format(amt=amt, usd=usd, m2=m2, price=price, pct=pct, months=months)
        fact_text = tpl[1].format(amt=amt, usd=usd, m2=m2, price=price, pct=pct, months=months)
        examples.append(example(
            nodes, pick_hint("same", "obra"), "obra", _prev_es(), msg,
            out("specific", "summary_only", "same", "obra",
                facts=[fact(lot_id, fact_text, "user")])
        ))
    return examples


def gen_g2_software():
    """Numeric facts — software."""
    examples = []
    templates_en = [
        ("API handles {n} requests per second with p99 at {ms}ms",
         "Throughput: {n} req/s, p99 latency: {ms}ms"),
        ("We have {pct}% test coverage across {n} test files",
         "Test coverage: {pct}%, {n} test files"),
        ("Sprint velocity is {n} story points, we're in sprint {sprint}",
         "Velocity: {n} points/sprint, current sprint: {sprint}"),
        ("Database has {n} million rows in the main table",
         "Main table: {n}M rows"),
        ("Monthly AWS bill is ${usd}, up {pct}% from last month",
         "AWS monthly cost: ${usd}, +{pct}% MoM"),
        ("Deployment takes {n} minutes, we deploy {freq} per day",
         "Deploy time: {n}min, frequency: {freq}/day"),
        ("The Docker image is {n}MB, we need to slim it down",
         "Docker image size: {n}MB"),
        ("We have {n} active users and {dau} DAU",
         "Active users: {n}, DAU: {dau}"),
    ]
    for _ in range(30):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        tpl = pick(templates_en)
        topic = proj[1].lower()
        n = str(random.choice([12, 45, 120, 500, 1200, 5000, 15000]))
        ms = str(random.choice([45, 120, 230, 450, 800]))
        pct = _pct()
        sprint = str(random.randint(5, 30))
        usd = _amount_usd()
        freq = str(random.choice([2, 3, 5, 8, 12]))
        dau = str(random.choice([500, 1200, 5000, 15000, 50000]))
        msg = tpl[0].format(n=n, ms=ms, pct=pct, sprint=sprint, usd=usd, freq=freq, dau=dau)
        fact_text = tpl[1].format(n=n, ms=ms, pct=pct, sprint=sprint, usd=usd, freq=freq, dau=dau)
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), msg,
            out("specific", "summary_only", "same", topic,
                facts=[fact(proj[0], fact_text, "user")])
        ))
    return examples


def gen_g2_health():
    """Numeric facts — health/family."""
    examples = []
    templates = [
        ("El nene pesa {kg}kg y mide {cm}cm, el pediatra dice que está bien",
         "Peso: {kg}kg, altura: {cm}cm, dentro de parámetros normales"),
        ("Le dieron {med} {dose}mg cada {hours} horas por {days} días",
         "Medicación: {med} {dose}mg cada {hours}h, {days} días"),
        ("El turno con el {especialista} es el {date} a las {time}",
         "Turno {especialista}: {date} a las {time}"),
        ("La obra social cubre el {pct}% del tratamiento",
         "Cobertura obra social: {pct}%"),
    ]
    for _ in range(12):
        nodes, parent, partner, child, city, clinic = health_family_graph_v4()
        tpl = pick(templates)
        kg = str(random.randint(8, 35))
        cm = str(random.randint(60, 140))
        med = pick(["Amoxicilina", "Ibuprofeno", "Paracetamol"])
        dose = str(random.choice([200, 400, 500, 600]))
        hours = str(random.choice([6, 8, 12]))
        days = str(random.choice([5, 7, 10, 14]))
        especialista = pick(MEDICAL)[1]
        date = f"{random.randint(1,28)}/{random.randint(1,12)}"
        time = f"{random.randint(8,18)}:{random.choice(['00','30'])}"
        pct = _pct()
        msg = tpl[0].format(kg=kg, cm=cm, med=med, dose=dose, hours=hours,
                            days=days, especialista=especialista, date=date,
                            time=time, pct=pct)
        fact_text = tpl[1].format(kg=kg, cm=cm, med=med, dose=dose, hours=hours,
                                  days=days, especialista=especialista, date=date,
                                  time=time, pct=pct)
        target = child[0] if "nene" in tpl[0] or "Le dieron" in tpl[0] else parent[0]
        examples.append(example(
            nodes, pick_hint("same", "salud familia"), "salud familia",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "salud familia",
                facts=[fact(target, fact_text, "user")])
        ))
    return examples


def gen_g2_travel():
    """Numeric facts — travel."""
    examples = []
    templates = [
        ("El vuelo {origin}-{dest} sale {usd} USD ida y vuelta",
         "Vuelo {origin}-{dest}: {usd} USD ida y vuelta"),
        ("El hotel en {barrio} cuesta {usd} USD/noche, reservé {nights} noches",
         "Hotel {barrio}: {usd} USD/noche, {nights} noches"),
        ("El presupuesto total del viaje es {usd} USD para {days} días",
         "Presupuesto viaje: {usd} USD, {days} días"),
        ("El seguro de viaje sale {usd} USD por persona",
         "Seguro viaje: {usd} USD/persona"),
        ("El tren {dest_a}-{dest_b} cuesta {eur} EUR",
         "Tren {dest_a}-{dest_b}: {eur} EUR"),
    ]
    for _ in range(12):
        nodes, person, city_origin, dest, trip_id, barrio = travel_graph_v4()
        tpl = pick(templates)
        usd = _amount_usd()
        nights = str(random.choice([3, 4, 5, 7, 10, 14]))
        days = str(random.choice([7, 10, 14, 21, 30]))
        eur = str(random.choice([25, 45, 80, 120, 180]))
        dest_b = pick([d for d in TRAVEL_DESTINATIONS if d != dest])
        msg = tpl[0].format(origin=city_origin[1], dest=dest[1], usd=usd,
                            barrio=barrio[1], nights=nights, days=days, eur=eur,
                            dest_a=dest[1], dest_b=dest_b[1])
        fact_text = tpl[1].format(origin=city_origin[1], dest=dest[1], usd=usd,
                                  barrio=barrio[1], nights=nights, days=days, eur=eur,
                                  dest_a=dest[1], dest_b=dest_b[1])
        examples.append(example(
            nodes, pick_hint("same", f"viaje a {dest[1]}"), f"viaje a {dest[1]}",
            _prev_es(), msg,
            out("specific", "summary_only", "same", f"viaje a {dest[1]}",
                facts=[fact(trip_id, fact_text, "user")])
        ))
    return examples


def gen_g2_trabajo():
    """Numeric facts — work/freelance."""
    examples = []
    templates = [
        ("Mi facturación este mes fue {amt} ARS, el cliente pagó a {days} días",
         "Facturación mensual: {amt} ARS, plazo de pago: {days} días"),
        ("Cobro {usd} USD/hora por este proyecto, {hours} horas semanales",
         "Rate: {usd} USD/hora, {hours}h/semana"),
        ("El proyecto lleva {months} meses y va por el {pct}% de avance",
         "Tiempo: {months} meses, avance: {pct}%"),
        ("Me deben {amt} ARS de facturas atrasadas",
         "Facturas pendientes: {amt} ARS"),
    ]
    for _ in range(12):
        nodes, person, project, client, city, tech = freelance_graph_v4()
        tpl = pick(templates)
        amt = _amount_ars()
        usd = str(random.choice([15, 25, 35, 50, 75, 100]))
        days = str(random.choice([15, 30, 45, 60]))
        hours = str(random.choice([10, 15, 20, 30, 40]))
        months = _months()
        pct = _pct()
        msg = tpl[0].format(amt=amt, usd=usd, days=days, hours=hours,
                            months=months, pct=pct)
        fact_text = tpl[1].format(amt=amt, usd=usd, days=days, hours=hours,
                                  months=months, pct=pct)
        examples.append(example(
            nodes, pick_hint("same", project[1].lower()), project[1].lower(),
            _prev_es(), msg,
            out("specific", "summary_only", "same", project[1].lower(),
                facts=[fact(project[0], fact_text, "user")])
        ))
    return examples


def gen_g2_literature():
    """Numeric facts — literature."""
    examples = []
    templates = [
        ("The first edition was published in {year} with {pages} pages",
         "First edition: {year}, {pages} pages"),
        ("{title} has been translated into {n} languages",
         "Translated into {n} languages"),
        ("Chapter {ch} is {pages} pages long, the longest in the book",
         "Chapter {ch}: {pages} pages (longest chapter)"),
    ]
    for _ in range(6):
        nodes, chars, places, title, key = literature_graph_v4()
        tpl = pick(templates)
        year = str(random.choice([1605, 1818, 1887, 1897, 1818, 800]))
        pages = str(random.choice([180, 250, 340, 420, 560, 780]))
        n = str(random.choice([12, 25, 40, 50, 80]))
        ch = str(random.randint(1, 30))
        char0 = chars[0]
        msg = tpl[0].format(year=year, pages=pages, n=n, title=title, ch=ch)
        fact_text = tpl[1].format(year=year, pages=pages, n=n, ch=ch)
        examples.append(example(
            nodes, pick_hint("same", title.lower()), title.lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", title.lower(),
                facts=[fact(char0[0], fact_text, "user")])
        ))
    return examples


def gen_g2_all():
    """Generate all G2 examples (~120)."""
    all_ex = []
    all_ex += gen_g2_finance()       # 30
    all_ex += gen_g2_construction()  # 18
    all_ex += gen_g2_software()      # 30
    all_ex += gen_g2_health()        # 12
    all_ex += gen_g2_travel()        # 12
    all_ex += gen_g2_trabajo()       # 12
    all_ex += gen_g2_literature()    # 6
    return all_ex


# ═══════════════════════════════════════════════════════════════════════════
# G3. Empty Output  (90 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g3_all():
    """Generate all empty output examples."""
    examples = []

    # --- Greetings (25) ---
    greetings_es = [
        "Hola!", "Buenas!", "Buenos días", "Buenas tardes", "Buenas noches",
        "Qué onda!", "Cómo andás?", "Todo bien?", "Hola, tanto tiempo!",
        "Ey!", "Qué tal?", "Hola hola",
    ]
    greetings_en = [
        "Hello!", "Hey there!", "Good morning", "Hi", "What's up?",
        "Hey!", "How's it going?", "Good afternoon", "Yo!",
        "Howdy", "How are you?", "Hi there", "Hello hello",
    ]
    for msg in greetings_es[:13]:
        nodes = [enode(pick(AR_CITIES)[0], pick(AR_CITIES)[1], "place")] if random.random() > 0.5 else []
        examples.append(example(
            nodes, pick_hint("query"), "null", None, msg,
            out("chat", "summary_only", "same", "")
        ))
    for msg in greetings_en[:12]:
        if random.random() > 0.5:
            nodes, proj, org, fe, be, db, people = software_graph_v4()
            topic = proj[1].lower()
        else:
            nodes, topic = [], ""
        examples.append(example(
            nodes, pick_hint("query"), topic or "null", None, msg,
            out("chat", "summary_only", "same", topic)
        ))

    # --- Smalltalk (25) ---
    smalltalk_es = [
        "Qué hora es?", "Está lindo afuera hoy", "Qué calor hace",
        "Me estoy tomando un café", "Ya es viernes!", "Qué embole",
        "Uf, qué semana", "Me duele la cabeza", "Necesito vacaciones",
        "Hoy no tengo ganas de nada", "Estoy cansado",
        "Pasame el mate", "Vamos a comer?",
    ]
    smalltalk_en = [
        "What time is it?", "Nice weather today", "I'm so tired",
        "Just having coffee", "TGIF!", "This week has been crazy",
        "I need a vacation", "I'm bored", "Ugh Mondays",
        "Can't wait for the weekend", "Anyone want lunch?",
        "It's so cold outside",
    ]
    for msg in smalltalk_es:
        nodes, person, city, funds = personal_finance_graph_v4()
        examples.append(example(
            nodes, pick_hint("query", "finanzas personales"), "finanzas personales",
            _prev_es(), msg,
            out("chat", "summary_only", "same", "finanzas personales")
        ))
    for msg in smalltalk_en:
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        examples.append(example(
            nodes, pick_hint("query", topic), topic, _prev_en(), msg,
            out("chat", "summary_only", "same", topic)
        ))

    # --- Meta-questions (20) ---
    meta_es = [
        "Podés buscar información por mí?", "Cómo funcionás?",
        "Qué podés hacer?", "Sos una IA?", "Cuánto sabés de mi grafo?",
        "Me podés ayudar con algo?", "Tenés memoria?",
        "Qué datos tenés guardados?", "Cómo se usa esto?",
        "Para qué sirve el grafo?",
    ]
    meta_en = [
        "Can you search the internet?", "How do you work?",
        "What can you help me with?", "Are you an AI?",
        "What data do you have about me?", "Can you remember things?",
        "How does this knowledge graph work?",
        "What's stored in the graph?", "Can you help me plan?",
        "What are your limitations?",
    ]
    for msg in meta_es:
        nodes = [enode(pick(AR_PERSONS)[0], pick(AR_PERSONS)[1], "person")] if random.random() > 0.5 else []
        examples.append(example(
            nodes, pick_hint("query"), "null", _prev_es(), msg,
            out("chat", "summary_only", "same", "")
        ))
    for msg in meta_en:
        nodes = [enode(pick(PROJECTS)[0], pick(PROJECTS)[1], "project")] if random.random() > 0.5 else []
        examples.append(example(
            nodes, pick_hint("query"), "null", _prev_en(), msg,
            out("chat", "summary_only", "same", "")
        ))

    # --- Opinions without data (20) ---
    opinions_es = [
        "Genial!", "Buenísimo", "Uf, qué estrés", "Me parece bien",
        "Qué buena onda", "No me convence mucho", "Puede ser",
        "Me gusta la idea", "Bárbaro", "Dale, me copa",
    ]
    opinions_en = [
        "Awesome!", "That's great", "Sounds good", "I like that",
        "Makes sense", "Interesting", "Cool!", "Nice",
        "That's fine", "Works for me",
    ]
    for msg in opinions_es:
        nodes, person, city, funds = personal_finance_graph_v4()
        examples.append(example(
            nodes, pick_hint("same", "finanzas personales"), "finanzas personales",
            _prev_es(), msg,
            out("chat", "summary_only", "same", "finanzas personales")
        ))
    for msg in opinions_en:
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), msg,
            out("chat", "summary_only", "same", topic)
        ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# G4. Relations  (90 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g4_all():
    """Generate all relation examples."""
    examples = []

    # --- located_in (15) ---
    for _ in range(8):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        msg = f"El {barrio[1]} queda en {city[1]}, zona residencial linda"
        examples.append(example(
            nodes, pick_hint("same", "compra terreno"), "compra terreno",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "compra terreno",
                relations=[r(barrio[0], city[0], "located_in")],
                facts=[fact(barrio[0], "Zona residencial", "user")])
        ))
    for _ in range(7):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        city_id, city_name = pick([("san_francisco", "San Francisco"), ("new_york", "New York"),
                                    ("austin", "Austin"), ("seattle", "Seattle")])
        nodes.append(enode(city_id, city_name, "place"))
        msg = f"{org[1]} headquarters are in {city_name}"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                relations=[r(org[0], city_id, "located_in")],
                facts=[fact(org[0], f"HQ: {city_name}", "user")])
        ))

    # --- works_at (10) ---
    for _ in range(5):
        nodes, person, project, client, city, tech = freelance_graph_v4()
        msg = f"Estoy trabajando full-time en {client[1]} ahora"
        examples.append(example(
            nodes, pick_hint("same", project[1].lower()), project[1].lower(),
            _prev_es(), msg,
            out("specific", "summary_only", "same", project[1].lower(),
                relations=[r(person[0], client[0], "works_at")])
        ))
    for _ in range(5):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        person = pick(people) if people else pick(PERSONS)
        msg = f"{person[1]} just joined {org[1]} as a senior engineer"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                relations=[r(person[0], org[0], "works_at")],
                facts=[fact(person[0], f"Role at {org[1]}: senior engineer", "user")])
        ))

    # --- uses_technology (10) ---
    for _ in range(5):
        nodes, person, project, client, city, tech = freelance_graph_v4()
        new_tech = pick(TECH_ES)
        msg = f"Estamos migrando {project[1]} a {new_tech[1]}"
        examples.append(example(
            nodes, pick_hint("same", project[1].lower()), project[1].lower(),
            _prev_es(), msg,
            out("specific", "summary_only", "same", project[1].lower(),
                entities=[ent(new_tech[0], new_tech[1], "technology", "UNIVERSAL",
                              f"{new_tech[1]} framework/tool")] if not any(n["id"] == new_tech[0] for n in nodes) else [],
                relations=[r(project[0], new_tech[0], "uses_technology")])
        ))
    for _ in range(5):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        new_tech = pick(LANGUAGES)
        msg = f"We're adding {new_tech[1]} to the {proj[1]} stack for the worker service"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                entities=[ent(new_tech[0], new_tech[1], "technology", "UNIVERSAL",
                              f"Programming language")] if not any(n["id"] == new_tech[0] for n in nodes) else [],
                relations=[r(proj[0], new_tech[0], "uses_technology")])
        ))

    # --- part_of (8) ---
    for _ in range(4):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        msg = f"El barrio {barrio[1]} es parte de {city[1]}, la zona más nueva"
        examples.append(example(
            nodes, pick_hint("same", "compra terreno"), "compra terreno",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "compra terreno",
                relations=[r(barrio[0], city[0], "part_of")],
                facts=[fact(barrio[0], "Zona más nueva de la ciudad", "user")])
        ))
    for _ in range(4):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        module = pick(["auth_module", "billing_module", "analytics_module", "search_module"])
        mod_label = module.replace("_", " ").title()
        msg = f"The {mod_label} is a core part of {proj[1]}, handles all user sessions"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                entities=[ent(module, mod_label, "project", "PERSONAL",
                              f"Core module in {proj[1]}")],
                relations=[r(module, proj[0], "part_of")])
        ))

    # --- created_by (5) ---
    for _ in range(3):
        nodes, chars, places, title, key = literature_graph_v4()
        author_map = {"sherlock": ("arthur_conan_doyle", "Arthur Conan Doyle"),
                      "quijote": ("miguel_cervantes", "Miguel de Cervantes"),
                      "odyssey": ("homer", "Homer"),
                      "gothic": ("bram_stoker", "Bram Stoker")}
        author = author_map.get(key, ("unknown_author", "Unknown Author"))
        msg = f"{title} was written by {author[1]}" if key != "quijote" else f"{title} fue escrito por {author[1]}"
        examples.append(example(
            nodes, pick_hint("same", title.lower()), title.lower(),
            _prev_en() if key != "quijote" else _prev_es(), msg,
            out("specific", "summary_only", "same", title.lower(),
                entities=[ent(author[0], author[1], "person", "UNIVERSAL",
                              f"Author of {title}")],
                relations=[r(chars[0][0], author[0], "created_by")])
        ))
    for _ in range(2):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        doc_id = f"{proj[0]}_docs"
        person = pick(people) if people else pick(PERSONS)
        msg = f"{person[1]} wrote the architecture decision record for {proj[1]}"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                entities=[ent(doc_id, f"{proj[1]} ADR", "document", "PERSONAL",
                              f"Architecture decision record for {proj[1]}")],
                relations=[r(doc_id, person[0], "created_by")])
        ))

    # --- serves (5) ---
    for _ in range(5):
        nodes, person, city, funds = personal_finance_graph_v4()
        fund = pick(funds)
        msg = f"El {fund[1]} es para mi ahorro de jubilación, me viene muy bien"
        examples.append(example(
            nodes, pick_hint("same", "inversiones"), "inversiones",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "inversiones",
                relations=[r(fund[0], person[0], "serves")],
                facts=[fact(fund[0], "Objetivo: ahorro jubilación", "user")])
        ))

    # --- depends_on (5) ---
    for _ in range(5):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        msg = f"{proj[1]} heavily depends on {db[1]} — if the DB goes down, everything stops"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                relations=[r(proj[0], db[0], "depends_on")],
                facts=[fact(proj[0], f"Critical dependency on {db[1]}", "user")])
        ))

    # --- maintains (5) ---
    for _ in range(5):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        person = pick(people) if people else pick(PERSONS)
        msg = f"{person[1]} is the primary maintainer of the {proj[1]} codebase"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                relations=[r(person[0], proj[0], "maintains")])
        ))

    # --- member_of (4) ---
    for _ in range(4):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        person = pick(people) if people else pick(PERSONS)
        msg = f"{person[1]} is a member of the {org[1]} engineering team"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                relations=[r(person[0], org[0], "member_of")])
        ))

    # --- deployed_on (3) ---
    for _ in range(3):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        cloud = pick(CLOUD)
        if not any(n["id"] == cloud[0] for n in nodes):
            nodes.append(enode(cloud[0], cloud[1], "technology"))
        msg = f"{proj[1]} is deployed on {cloud[1]}, using their managed Kubernetes"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                relations=[r(proj[0], cloud[0], "deployed_on")],
                facts=[fact(proj[0], f"Uses managed Kubernetes on {cloud[1]}", "user")])
        ))

    # --- alternative_to (3) ---
    for _ in range(3):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        alt_fe = pick([f for f in FRONTEND if f != fe])
        msg = f"We considered {alt_fe[1]} as an alternative to {fe[1]} for {proj[1]}"
        if not any(n["id"] == alt_fe[0] for n in nodes):
            nodes.append(enode(alt_fe[0], alt_fe[1], "technology"))
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                relations=[r(alt_fe[0], fe[0], "alternative_to")])
        ))

    # --- produces (3) ---
    for _ in range(3):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        product = pick(["api_service", "mobile_app", "admin_dashboard", "public_site"])
        product_label = product.replace("_", " ").title()
        msg = f"{org[1]} produces the {product_label} that powers {proj[1]}"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                entities=[ent(product, product_label, "project", "PERSONAL",
                              f"Product by {org[1]}")],
                relations=[r(org[0], product, "produces")])
        ))

    # --- documented_in (3) ---
    for _ in range(3):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        doc = pick(["readme", "adr_001", "wiki_page", "confluence_doc"])
        doc_label = doc.replace("_", " ").title()
        msg = f"The {proj[1]} architecture is documented in the {doc_label}"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                entities=[ent(doc, doc_label, "document", "PERSONAL",
                              f"Documentation for {proj[1]}")],
                relations=[r(proj[0], doc, "documented_in")])
        ))

    # --- participated_in (3) ---
    for _ in range(3):
        nodes, person, city_origin, dest, trip_id, barrio = travel_graph_v4()
        msg = f"Fui a la {pick(TRAVEL_ATTRACTIONS)[1]} cuando estuve en {dest[1]}"
        examples.append(example(
            nodes, pick_hint("same", f"viaje a {dest[1]}"), f"viaje a {dest[1]}",
            _prev_es(), msg,
            out("specific", "summary_only", "same", f"viaje a {dest[1]}",
                relations=[r(person[0], trip_id, "participated_in")])
        ))

    # --- resulted_in (3) ---
    for _ in range(3):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        incident = f"{proj[0]}_outage"
        msg = f"Last week's deploy resulted in a 2-hour outage for {proj[1]}"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                entities=[ent(incident, f"{proj[1]} Outage", "event", "PERSONAL",
                              f"Production outage for {proj[1]}")],
                relations=[r(incident, proj[0], "resulted_in")],
                facts=[fact(incident, "Duration: 2 hours, caused by deploy", "user")])
        ))

    # --- triggered_by (2) ---
    for _ in range(2):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        incident = f"{proj[0]}_incident"
        msg = f"The {proj[1]} performance regression was triggered by the database migration"
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("specific", "summary_only", "same", proj[1].lower(),
                entities=[ent(incident, f"{proj[1]} Regression", "event", "PERSONAL",
                              f"Performance regression in {proj[1]}")],
                relations=[r(incident, db[0], "triggered_by")],
                facts=[fact(incident, "Triggered by database migration", "user")])
        ))

    # --- NEGATIVE EXAMPLES (15) ---
    # "needs" -> uses_technology (create redis as new entity)
    for _ in range(2):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(),
            f"The project needs Redis for caching",
            out("specific", "summary_only", "same", topic,
                entities=[ent("redis", "Redis", "technology", "UNIVERSAL",
                              "In-memory data store for caching")],
                relations=[r(proj[0], "redis", "uses_technology")],
                facts=[fact(proj[0], "Redis needed for caching", "user")])
        ))

    # "near" -> fact only (no relation)
    for _ in range(2):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        examples.append(example(
            nodes, pick_hint("same", "compra terreno"), "compra terreno",
            _prev_es(), "La casa está cerca del colegio",
            out("specific", "summary_only", "same", "compra terreno",
                facts=[fact(lot_id, "Cerca del colegio", "user")])
        ))

    # "produced_by" -> created_by (create doc entity first)
    for _ in range(2):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        doc_id = f"{proj[0]}_api_docs"
        person = pick(people) if people else pick(PERSONS)
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(),
            f"The API docs were produced by {person[1]}",
            out("specific", "summary_only", "same", topic,
                entities=[ent(doc_id, f"{proj[1]} API Docs", "document", "PERSONAL",
                              f"API documentation for {proj[1]}")],
                relations=[r(doc_id, person[0], "created_by")])
        ))

    # "visited" -> fact only (no relation)
    for _ in range(2):
        nodes, person, city_origin, dest, trip_id, barrio = travel_graph_v4()
        attraction = pick(TRAVEL_ATTRACTIONS)
        examples.append(example(
            nodes, pick_hint("same", f"viaje a {dest[1]}"), f"viaje a {dest[1]}",
            _prev_es(), f"Visitamos la {attraction[1]} ayer",
            out("specific", "summary_only", "same", f"viaje a {dest[1]}",
                facts=[fact(trip_id, f"Visitó {attraction[1]}", "user")])
        ))

    # "supports" -> fact only (no relation)
    for _ in range(2):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(),
            "The app supports dark mode and RTL layouts",
            out("specific", "summary_only", "same", topic,
                facts=[fact(proj[0], "Supports dark mode and RTL layouts", "user")])
        ))

    # "owns" -> fact only (no relation)
    for _ in range(2):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        examples.append(example(
            nodes, pick_hint("same", "propiedades"), "propiedades",
            _prev_es(), "Tengo 3 propiedades en Córdoba",
            out("specific", "summary_only", "same", "propiedades",
                facts=[fact(person[0], "Posee 3 propiedades en Córdoba", "user")])
        ))

    # "works_with" -> member_of (person -> org, not person -> project)
    for _ in range(2):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        person = pick(people) if people else pick(PERSONS)
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(),
            f"{person[1]} works with the design team at {org[1]}",
            out("specific", "summary_only", "same", topic,
                relations=[r(person[0], org[0], "member_of")])
        ))

    # "has_document" -> documented_in
    nodes, proj, org, fe, be, db, people = software_graph_v4()
    doc_id = f"{proj[0]}_spec"
    examples.append(example(
        nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
        _prev_en(),
        f"The project has a detailed spec document covering all requirements",
        out("specific", "summary_only", "same", proj[1].lower(),
            entities=[ent(doc_id, f"{proj[1]} Spec", "document", "PERSONAL",
                          f"Requirements specification for {proj[1]}")],
            relations=[r(proj[0], doc_id, "documented_in")])
    ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# G5. Topic Changes  (60 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g5_all():
    """Generate topic change, subtopic, and first-message examples."""
    examples = []

    # --- Topic changed (30) ---
    change_pairs_es = [
        ("finanzas personales", "compra terreno", "Dejemos lo de la plata. Necesito contarte del terreno que estamos viendo"),
        ("obra", "viaje a Europa", "Cambiando de tema, estoy planeando un viaje a Europa con la familia"),
        ("salud familia", "trabajo", "Bueno, pasemos al laburo. Tengo un proyecto nuevo"),
        ("inversiones", "fitness", "Ey, cambiemos de tema. Empecé el gimnasio esta semana"),
        ("viaje a Roma", "finanzas personales", "Volviendo a lo de guita, necesito revisar mis inversiones"),
    ]
    change_pairs_en = [
        ("beacon project", "atlas project", "Let's switch gears. I want to talk about the Atlas project now"),
        ("atlas project", "hiring", "Changing topic — we need to discuss hiring for Q3"),
        ("deployment", "code review", "Actually, let me bring up something else. Can we talk about the code review process?"),
        ("backend architecture", "frontend redesign", "Let's move on to the frontend redesign"),
        ("performance", "security", "We should talk about security instead, there's a vulnerability we found"),
    ]
    for old_topic, new_topic, msg in change_pairs_es:
        for _ in range(3):
            # Pick appropriate graph based on new topic
            if "terreno" in new_topic:
                nodes = real_estate_graph_v4()[0]
            elif "viaje" in new_topic:
                nodes = travel_graph_v4()[0]
            elif "trabajo" in new_topic or "proyecto" in new_topic:
                nodes = freelance_graph_v4()[0]
            elif "fitness" in new_topic or "gimnasio" in new_topic:
                nodes = [enode(pick(AR_PERSONS)[0], pick(AR_PERSONS)[1], "person")]
            else:
                nodes = personal_finance_graph_v4()[0]
            examples.append(example(
                nodes, pick_hint("changed"), old_topic, _prev_es(), msg,
                out("specific", "summary_only", "changed", new_topic)
            ))

    for old_topic, new_topic, msg in change_pairs_en:
        for _ in range(3):
            nodes, proj, org, fe, be, db, people = software_graph_v4()
            examples.append(example(
                nodes, pick_hint("changed"), old_topic, _prev_en(), msg,
                out("specific" if "discuss" in msg or "talk" in msg else "overview",
                    "summary_only", "changed", new_topic)
            ))

    # --- Subtopic (20) ---
    subtopic_es = [
        ("compra terreno", "planos", "Hablemos específicamente de los planos. ¿Ya tenemos algo?"),
        ("finanzas personales", "inversiones en CEDEARs", "Puntualmente, quiero hablar de los CEDEARs que tengo"),
        ("obra", "materiales de construcción", "Enfoquémonos en los materiales. ¿Cuánto sale el hierro?"),
        ("salud familia", "vacunas", "Vamos al tema de las vacunas del nene"),
    ]
    subtopic_en = [
        ("beacon project", "beacon database layer", "Let's dig into the database layer specifically"),
        ("atlas project", "atlas API design", "I want to focus on the API design for Atlas"),
        ("deployment", "CI/CD pipeline", "Let's zoom into the CI/CD pipeline configuration"),
        ("architecture", "authentication flow", "Can we focus on the auth flow?"),
        ("performance", "database query optimization", "Let's look specifically at DB query performance"),
        ("security", "API rate limiting", "I want to drill into the rate limiting strategy"),
    ]
    for parent_topic, sub_topic, msg in subtopic_es:
        for _ in range(2):
            if "terreno" in parent_topic or "obra" in parent_topic:
                nodes = real_estate_graph_v4()[0]
            elif "finanzas" in parent_topic:
                nodes = personal_finance_graph_v4()[0]
            else:
                nodes = health_family_graph_v4()[0]
            examples.append(example(
                nodes, pick_hint("subtopic", parent_topic), parent_topic,
                _prev_es(), msg,
                out("specific", "with_chunks", "subtopic", sub_topic)
            ))
    for parent_topic, sub_topic, msg in subtopic_en:
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        examples.append(example(
            nodes, pick_hint("subtopic", parent_topic), parent_topic,
            _prev_en(), msg,
            out("specific", "with_chunks", "subtopic", sub_topic)
        ))
    # pad to ~20
    for _ in range(20 - len(subtopic_es)*2 - len(subtopic_en)):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        parent = proj[1].lower()
        sub = f"{proj[1].lower()} {pick(['frontend', 'backend', 'testing', 'deploy'])}"
        msg = f"Let's focus on the {sub.split()[-1]} part of {proj[1]}"
        examples.append(example(
            nodes, pick_hint("subtopic", parent), parent, _prev_en(), msg,
            out("specific", "with_chunks", "subtopic", sub)
        ))

    # --- First message (10) ---
    first_msgs_es = [
        ("Hola! Necesito trackear la compra de un terreno en Cipolletti",
         "compra terreno"),
        ("Estoy arrancando un proyecto nuevo con React y Supabase",
         "proyecto nuevo"),
        ("Quiero llevar registro de mis inversiones",
         "inversiones"),
        ("Empezamos a planificar el viaje a Europa para diciembre",
         "viaje a Europa"),
        ("Necesito organizar la información del tratamiento de mi hijo",
         "salud hijo"),
    ]
    first_msgs_en = [
        ("I'm starting a new project called Beacon, it's a dashboard app",
         "beacon project"),
        ("I want to track our team's hiring pipeline",
         "hiring pipeline"),
        ("Let me tell you about our tech stack and architecture",
         "tech stack"),
        ("I need to organize information about our upcoming product launch",
         "product launch"),
        ("Starting to document our microservices architecture",
         "architecture"),
    ]
    for msg, topic in first_msgs_es:
        examples.append(example(
            [], "unresolved — classify the topic yourself", "null", None, msg,
            out("specific", "summary_only", "changed", topic)
        ))
    for msg, topic in first_msgs_en:
        examples.append(example(
            [], "unresolved — classify the topic yourself", "null", None, msg,
            out("specific", "summary_only", "changed", topic)
        ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# G6. Dedup & Corrections  (60 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g6_all():
    """Generate dedup and correction examples."""
    examples = []

    # --- Alias resolution (25) ---
    alias_es = [
        ("la base", "database", "PostgreSQL"), ("la app", "project", None),
        ("el arq", "person", None), ("la constructora", "organization", None),
        ("el fondo", "concept", None), ("el laburo", "project", None),
        ("mi viejo", "person", None), ("la clínica", "organization", None),
    ]
    for _ in range(12):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        alias = pick([("el arq", architect), ("la constructora", builder),
                       ("el terreno", (lot_id, f"Terreno en {barrio[1]}"))])
        amt = _amount_usd()
        msg = f"{alias[0].capitalize()} nos mandó un presupuesto actualizado de {amt} USD"
        examples.append(example(
            nodes, pick_hint("same", "obra"), "obra", _prev_es(), msg,
            out("specific", "summary_only", "same", "obra",
                facts=[fact(alias[1][0], f"Presupuesto actualizado: {amt} USD", "user")])
        ))

    for _ in range(13):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        alias_pairs = [
            ("the app", proj), ("the database", db), ("the frontend", fe),
            ("the backend", be), ("the company", org),
        ]
        alias = pick(alias_pairs)
        pct = _pct()
        msg = f"We need to optimize {alias[0]}, it's consuming {pct}% more memory than expected"
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), msg,
            out("specific", "with_chunks", "same", topic,
                facts=[fact(alias[1][0], f"Memory usage: +{pct}% above expected", "user")])
        ))

    # --- Corrections (20) ---
    for _ in range(10):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        old_price = _amount_usd()
        new_price = str(int(old_price.replace(",", "")) - random.randint(2000, 5000))
        corrections = [
            f"Ojo, el terreno no era {old_price} USD, era {new_price} USD. El vendedor bajó el precio",
            f"Me equivoqué antes, el presupuesto es {new_price} USD no {old_price} USD",
            f"Corregime: el terreno tiene 450m2, no 400m2 como dije antes",
        ]
        msg = pick(corrections)
        examples.append(example(
            nodes, pick_hint("same", "compra terreno"), "compra terreno",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "compra terreno",
                facts=[fact(lot_id, msg.split(",")[0].replace("Ojo, ", "").replace("Me equivoqué antes, ", "").replace("Corregime: ", ""), "user")])
        ))

    for _ in range(10):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        corrections = [
            f"Actually, we switched from {fe[1]} to Vue for {proj[1]}",
            f"Wait, I was wrong — {proj[1]} uses {pick(DATABASES)[1]}, not {db[1]}",
            f"Correction: the team size is 8, not 5 like I said before",
        ]
        msg = pick(corrections)
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), msg,
            out("specific", "summary_only", "same", topic,
                facts=[fact(proj[0], msg.replace("Actually, ", "").replace("Wait, I was wrong — ", "").replace("Correction: ", ""), "user")])
        ))

    # --- Merge hints (15) ---
    for _ in range(8):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        # Add a "duplicate" node
        dup_id = f"{proj[0]}_dashboard"
        dup_label = f"{proj[1]} Dashboard"
        nodes.append(enode(dup_id, dup_label, "project"))
        msg = f"The {dup_label} is actually just {proj[1]}, they're the same thing"
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), msg,
            out("specific", "summary_only", "same", topic,
                entities=[ent(dup_id, dup_label, "project", "PERSONAL",
                              f"Same as {proj[1]}", existing_id=proj[0])],
                facts=[fact(proj[0], f"{dup_label} is an alias for {proj[1]}", "user")])
        ))

    for _ in range(7):
        nodes, person, city, funds = personal_finance_graph_v4()
        fund = pick(funds)
        alias_name = fund[1] + " de Galicia"
        alias_id = _id(alias_name)
        msg = f"El {alias_name} es el mismo {fund[1]} que ya tenemos, es del Banco Galicia"
        examples.append(example(
            nodes, pick_hint("same", "inversiones"), "inversiones",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "inversiones",
                entities=[ent(alias_id, alias_name, "concept", "PERSONAL",
                              f"Alias de {fund[1]} en Banco Galicia", existing_id=fund[0])],
                facts=[fact(fund[0], "Operado a través de Banco Galicia", "user")])
        ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# G7. Multi-Entity Complex  (30 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g7_all():
    """Generate multi-entity complex examples."""
    examples = []

    # --- 3+ new entities with cross-relations (15) ---
    for _ in range(8):
        nodes, proj_existing, org, fe, be, db, people = software_graph_v4()
        topic = "new project"
        proj_name = pick(["Phoenix", "Olympus", "Titan", "Mercury", "Neptune"])
        proj_id = _id(proj_name)
        tech1 = pick(LANGUAGES)
        tech2 = pick([t for t in FRONTEND if t != fe])
        cloud = pick(CLOUD)
        person = pick([p for p in PERSONS if p not in people])
        msg = (f"We just kicked off Project {proj_name} — it's built with {tech1[1]} "
               f"and {tech2[1]}, deployed on {cloud[1]}. {person[1]} is the lead.")
        examples.append(example(
            [enode(org[0], org[1], "organization")],
            pick_hint("changed"), "null", None, msg,
            out("specific", "summary_only", "changed", f"project {proj_name.lower()}",
                entities=[
                    ent(proj_id, f"Project {proj_name}", "project", "PERSONAL",
                        f"New project at {org[1]}"),
                    ent(tech1[0], tech1[1], "technology", "UNIVERSAL", f"Programming language"),
                    ent(tech2[0], tech2[1], "technology", "UNIVERSAL", f"Frontend framework"),
                    ent(cloud[0], cloud[1], "technology", "UNIVERSAL", "Cloud platform"),
                    ent(person[0], person[1], "person", "PERSONAL",
                        f"Lead for Project {proj_name}"),
                ],
                relations=[
                    r(proj_id, org[0], "part_of"),
                    r(proj_id, tech1[0], "uses_technology"),
                    r(proj_id, tech2[0], "uses_technology"),
                    r(proj_id, cloud[0], "deployed_on"),
                    r(person[0], proj_id, "maintains"),
                ])
        ))

    for _ in range(7):
        nodes, person, city, barrio, architect, builder, lot_id = real_estate_graph_v4()
        electrician = pick([p for p in AR_PERSONS if p != person and p != architect])
        plumber_name = pick(["Matías Ruiz", "Pablo Giménez", "Diego Sosa"])
        plumber_id = _id(plumber_name)
        material = pick(["porcelanato", "cemite", "ladrillo_hueco"])
        material_label = material.replace("_", " ").title()
        amt1 = _amount_usd()
        amt2 = _amount_ars()
        msg = (f"Para la obra contratamos al electricista {electrician[1]} "
               f"y al plomero {plumber_name}. Los materiales del corralón "
               f"salen {amt2} ARS, y el electricista cobra {amt1} USD.")
        examples.append(example(
            nodes, pick_hint("same", "obra"), "obra", _prev_es(), msg,
            out("specific", "summary_only", "same", "obra",
                entities=[
                    ent(electrician[0], electrician[1], "person", "PERSONAL",
                        "Electricista para la obra"),
                    ent(plumber_id, plumber_name, "person", "PERSONAL",
                        "Plomero para la obra"),
                ],
                facts=[
                    fact(electrician[0], f"Presupuesto: {amt1} USD", "user"),
                    fact(lot_id, f"Materiales corralón: {amt2} ARS", "user"),
                ])
        ))

    # --- Mix of new entities + facts on existing (15) ---
    for _ in range(8):
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        topic = proj[1].lower()
        new_person = pick([p for p in PERSONS if p not in people])
        job = pick(JOB_TITLES)
        n_users = str(random.choice([1000, 5000, 10000, 50000]))
        deploy_freq = str(random.choice([2, 5, 10]))
        msg = (f"{new_person[1]} joined as {job}. Also, {proj[1]} now has "
               f"{n_users} active users and we deploy {deploy_freq} times per day.")
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_en(), msg,
            out("specific", "summary_only", "same", topic,
                entities=[ent(new_person[0], new_person[1], "person", "PERSONAL",
                              f"New {job} on {proj[1]}")],
                relations=[r(new_person[0], proj[0], "maintains")],
                facts=[
                    fact(proj[0], f"Active users: {n_users}", "user"),
                    fact(proj[0], f"Deploy frequency: {deploy_freq}/day", "user"),
                ])
        ))

    for _ in range(7):
        nodes, person, city, funds = personal_finance_graph_v4()
        new_fund = pick([f for f in FIN_INSTRUMENTS if f not in funds])
        amt = _amount_ars()
        existing_fund = pick(funds)
        pct = _pct()
        msg = (f"Abrí un {new_fund[1]} nuevo y le metí {amt} ARS. "
               f"El {existing_fund[1]} me rindió {pct}% este trimestre.")
        examples.append(example(
            nodes, pick_hint("same", "inversiones"), "inversiones",
            _prev_es(), msg,
            out("specific", "summary_only", "same", "inversiones",
                entities=[ent(new_fund[0], new_fund[1], new_fund[2], "PERSONAL",
                              f"Nuevo instrumento financiero de {person[1]}")],
                facts=[
                    fact(new_fund[0], f"Inversión inicial: {amt} ARS", "user"),
                    fact(existing_fund[0], f"Rendimiento trimestral: {pct}%", "user"),
                ])
        ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# G8. Intent Balance + Spanish Boost  (~40 examples)
#     Adds overview, followup intents and more Spanish content
# ═══════════════════════════════════════════════════════════════════════════

def gen_g8_intent_balance():
    """Add overview & followup intents, and extra Spanish examples."""
    examples = []

    # --- Overview intent (15) ---
    overview_en = [
        ("Give me an overview of {proj}", "project overview"),
        ("What's the current state of {proj}?", "project status"),
        ("How many services does {proj} have?", "architecture overview"),
        ("Summarize the tech stack for {proj}", "tech stack"),
        ("What teams are working on {proj}?", "team overview"),
    ]
    for msg_tpl, topic_label in overview_en:
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        msg = msg_tpl.format(proj=proj[1])
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("overview", "summary_only", "same", proj[1].lower())
        ))

    overview_es = [
        ("Dame un resumen de mis inversiones", "inversiones"),
        ("Cómo está el tema del terreno?", "compra terreno"),
        ("Cuánta plata tengo invertida en total?", "finanzas personales"),
        ("Cómo viene la obra en general?", "obra"),
        ("Resumime el viaje hasta ahora", "viaje"),
        ("Qué tenemos registrado de la salud del nene?", "salud familia"),
        ("Cómo van los proyectos freelance?", "trabajo freelance"),
        ("Cuántos gastos tengo este mes?", "gastos mensuales"),
        ("Dame el estado general de todo", "resumen general"),
        ("Qué tengo anotado del tratamiento?", "salud familia"),
    ]
    for msg, topic in overview_es:
        if "inversiones" in topic or "finanzas" in topic or "gastos" in topic:
            nodes = personal_finance_graph_v4()[0]
        elif "terreno" in topic or "obra" in topic:
            nodes = real_estate_graph_v4()[0]
        elif "viaje" in topic:
            nodes = travel_graph_v4()[0]
        elif "salud" in topic:
            nodes = health_family_graph_v4()[0]
        elif "trabajo" in topic or "freelance" in topic:
            nodes = freelance_graph_v4()[0]
        else:
            nodes = personal_finance_graph_v4()[0]
        examples.append(example(
            nodes, pick_hint("query", topic), topic, _prev_es(), msg,
            out("overview", "summary_only", "same", topic)
        ))

    # --- Followup intent (15) ---
    followup_en = [
        ("Tell me more about that", "project details"),
        ("Can you expand on the deployment?", "deployment"),
        ("What else do we know about {db}?", "database details"),
        ("Go on, what about the testing strategy?", "testing"),
        ("You mentioned {fe} earlier — what version are we on?", "frontend"),
    ]
    for msg_tpl, topic_label in followup_en:
        nodes, proj, org, fe, be, db, people = software_graph_v4()
        msg = msg_tpl.format(db=db[1], fe=fe[1], proj=proj[1])
        examples.append(example(
            nodes, pick_hint("same", proj[1].lower()), proj[1].lower(),
            _prev_en(), msg,
            out("followup", "with_chunks", "same", proj[1].lower())
        ))

    followup_es = [
        ("Contame más de eso", "detalles"),
        ("Seguí con lo del presupuesto", "presupuesto"),
        ("Y qué más sabemos del terreno?", "compra terreno"),
        ("Ampliame lo del fondo", "inversiones"),
        ("Qué más hay del tratamiento del nene?", "salud familia"),
        ("Seguí con lo del viaje", "viaje"),
        ("Y qué onda con el proyecto?", "proyecto"),
        ("Decime más sobre el arquitecto", "obra"),
        ("Y la constructora qué dijo?", "obra"),
        ("Seguí, qué más tenemos?", "general"),
    ]
    for msg, topic in followup_es:
        if "inversiones" in topic or "presupuesto" in topic:
            nodes = personal_finance_graph_v4()[0]
        elif "terreno" in topic or "obra" in topic:
            nodes = real_estate_graph_v4()[0]
        elif "viaje" in topic:
            nodes = travel_graph_v4()[0]
        elif "salud" in topic:
            nodes = health_family_graph_v4()[0]
        elif "proyecto" in topic:
            nodes = freelance_graph_v4()[0]
        else:
            nodes = personal_finance_graph_v4()[0]
        examples.append(example(
            nodes, pick_hint("same", topic), topic, _prev_es(), msg,
            out("followup", "with_chunks", "same", topic)
        ))

    # --- Spanish software domain (boost language balance) (20) ---
    sw_es_templates = [
        ("Estamos usando {tech} para el proyecto {proj}, anda muy bien",
         lambda nodes, proj, tech: out("specific", "summary_only", "same", proj[1].lower(),
             relations=[r(proj[0], tech[0], "uses_technology")] if any(n["id"] == tech[0] for n in nodes) else [],
             entities=[] if any(n["id"] == tech[0] for n in nodes) else
                 [ent(tech[0], tech[1], "technology", "UNIVERSAL", f"Herramienta de desarrollo")],
             facts=[fact(proj[0], f"Usa {tech[1]}, funciona bien", "user")])),
        ("El deploy de {proj} se rompió ayer, tardamos 3 horas en arreglarlo",
         lambda nodes, proj, tech: out("specific", "summary_only", "same", proj[1].lower(),
             facts=[fact(proj[0], "Deploy fallido, 3 horas de downtime", "user")])),
        ("{person} se sumó al equipo de {proj} como developer",
         lambda nodes, proj, tech, person=None: out("specific", "summary_only", "same", proj[1].lower(),
             relations=[r(person[0] if person else "placeholder", proj[0], "maintains")],
             facts=[fact(proj[0], f"Nuevo developer: {person[1] if person else 'N/A'}", "user")])),
        ("La API de {proj} procesa {n} requests por segundo ahora",
         lambda nodes, proj, tech, n=None: out("specific", "summary_only", "same", proj[1].lower(),
             facts=[fact(proj[0], f"Throughput: {n} req/s", "user")])),
    ]
    for _ in range(20):
        nodes, person, project, client, city, tech = freelance_graph_v4()
        tech_item = pick(tech) if tech else pick(TECH_ES)
        tpl_idx = random.randint(0, 3)
        if tpl_idx == 0:
            msg = sw_es_templates[0][0].format(tech=tech_item[1], proj=project[1])
            output = sw_es_templates[0][1](nodes, project, tech_item)
        elif tpl_idx == 1:
            msg = sw_es_templates[1][0].format(proj=project[1])
            output = sw_es_templates[1][1](nodes, project, tech_item)
        elif tpl_idx == 2:
            new_person = pick(AR_PERSONS)
            msg = f"{new_person[1]} se sumó al equipo de {project[1]} como developer"
            output = out("specific", "summary_only", "same", project[1].lower(),
                entities=[ent(new_person[0], new_person[1], "person", "PERSONAL",
                              f"Developer en {project[1]}")] if not any(n["id"] == new_person[0] for n in nodes) else [],
                relations=[r(new_person[0], project[0], "maintains")],
                facts=[fact(project[0], f"Nuevo developer: {new_person[1]}", "user")])
        else:
            n_req = str(random.choice([500, 1200, 3000, 8000]))
            msg = f"La API de {project[1]} procesa {n_req} requests por segundo ahora"
            output = out("specific", "summary_only", "same", project[1].lower(),
                facts=[fact(project[0], f"Throughput: {n_req} req/s", "user")])
        examples.append(example(
            nodes, pick_hint("same", project[1].lower()), project[1].lower(),
            _prev_es(), msg, output
        ))

    # --- Spanish literature domain (10) ---
    lit_es_msgs = [
        ("Don Quijote confunde los molinos de viento con gigantes en el capítulo 8",
         "quijote", "don_quijote", "Confunde molinos con gigantes (cap. 8)"),
        ("Sancho Panza le dice que son molinos, pero Don Quijote no le cree",
         "quijote", "sancho_panza", "Advierte sobre los molinos pero no le creen"),
        ("Dulcinea es el amor idealizado de Don Quijote, nunca la ve realmente",
         "quijote", "dulcinea", "Amor idealizado, nunca la encuentra en persona"),
        ("Holmes deduce la profesión del visitante por las manchas en sus manos",
         "sherlock", "sherlock_holmes", "Deduce profesiones por detalles físicos"),
        ("Watson narra las aventuras desde su perspectiva de médico",
         "sherlock", "dr_watson", "Narrador de las historias, perspectiva médica"),
        ("Odiseo tarda 10 años en volver a Ítaca después de Troya",
         "odyssey", "odysseus", "Viaje de regreso: 10 años post-Troya"),
        ("Penélope teje y desteje esperando el regreso de Odiseo",
         "odyssey", "penelope", "Teje y desteje como estrategia de espera"),
        ("El Conde Drácula viaja a Londres para expandir su dominio",
         "gothic", "dracula", "Viaja a Londres buscando nuevas víctimas"),
        ("Van Helsing es el experto que lidera la caza del vampiro",
         "gothic", "van_helsing", "Lidera la caza de Drácula"),
        ("Frankenstein crea a la criatura en la Universidad de Ingolstadt",
         "gothic", "frankenstein", "Crea al monstruo en Ingolstadt"),
    ]
    for msg, key, char_id, fact_text in lit_es_msgs:
        nodes, chars, places, title, _ = literature_graph_v4()
        # Override key to match our message
        target_id = char_id if any(n["id"] == char_id for n in nodes) else chars[0][0]
        examples.append(example(
            nodes, pick_hint("same", title.lower()), title.lower(),
            _prev_es(), msg,
            out("specific", "summary_only", "same", title.lower(),
                facts=[fact(target_id, fact_text, "user")])
        ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# Main — Generate, Validate, Write
# ═══════════════════════════════════════════════════════════════════════════

def validate_example_v4(ex, idx, group_name):
    """Validate a single example against V4 schema + cross-references."""
    errors = []
    try:
        assistant_content = ex["messages"][2]["content"]
        ok, result = validate_s1_v4(assistant_content)
        if not ok:
            errors.append(f"[{group_name} #{idx}] Schema: {result}")
            return errors

        # Cross-reference validation
        user_content = ex["messages"][1]["content"]
        # Parse existing nodes from user content
        existing_nodes = []
        prefix = "EXISTING NODES:\n"
        if prefix in user_content:
            start = user_content.index(prefix) + len(prefix)
            end = user_content.find("\n\n", start)
            if end == -1:
                end = len(user_content)
            try:
                existing_nodes = json.loads(user_content[start:end])
            except json.JSONDecodeError:
                pass

        output = json.loads(assistant_content)
        xref_errors = validate_cross_references(output, existing_nodes)
        for e in xref_errors:
            errors.append(f"[{group_name} #{idx}] XRef: {e}")
    except Exception as e:
        errors.append(f"[{group_name} #{idx}] Error: {e}")
    return errors


def write_jsonl(examples, filename, group_name):
    """Write examples to JSONL, validate each, and return error count."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    all_errors = []
    with open(path, "w", encoding="utf-8") as f:
        for i, ex in enumerate(examples):
            errs = validate_example_v4(ex, i + 1, group_name)
            all_errors.extend(errs)
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    return path, all_errors


def main():
    parser = argparse.ArgumentParser(description="Generate V4 S1 training data")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    random.seed(args.seed)

    print("=" * 60)
    print("Generating V4 S1 Training Data")
    print("=" * 60)

    groups = {
        "g1_json_discipline": gen_g1_all,
        "g2_numeric_facts": gen_g2_all,
        "g3_empty_output": gen_g3_all,
        "g4_relations": gen_g4_all,
        "g5_topic_changes": gen_g5_all,
        "g6_dedup_corrections": gen_g6_all,
        "g7_multi_entity": gen_g7_all,
        "g8_intent_balance": gen_g8_intent_balance,
    }

    all_examples = []
    all_errors = []
    total_by_group = {}

    for name, gen_fn in groups.items():
        print(f"\n--- {name} ---")
        examples = gen_fn()
        total_by_group[name] = len(examples)
        print(f"  Generated: {len(examples)} examples")

        path, errors = write_jsonl(examples, f"v4_{name}.jsonl", name)
        print(f"  Written to: {path}")
        if errors:
            print(f"  ERRORS ({len(errors)}):")
            for e in errors[:5]:
                print(f"    {e}")
            if len(errors) > 5:
                print(f"    ... and {len(errors) - 5} more")
        else:
            print(f"  All {len(examples)} examples validated OK")
        all_errors.extend(errors)
        all_examples.extend(examples)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nTotal examples: {len(all_examples)}")
    for name, count in total_by_group.items():
        pct = count / len(all_examples) * 100
        print(f"  {name}: {count} ({pct:.1f}%)")

    if all_errors:
        print(f"\nTOTAL ERRORS: {len(all_errors)}")
        for e in all_errors[:10]:
            print(f"  {e}")
    else:
        print(f"\nAll {len(all_examples)} examples passed validation!")

    # Language stats
    es_count = 0
    en_count = 0
    es_markers = ["el ", "la ", "los ", "las ", "del ", "al ", "que ", "con ",
                   "por ", "para ", "está ", "tiene ", "vamos", "tengo", "necesito"]
    for ex in all_examples:
        user_msg = ex["messages"][1]["content"].split("USER: ")[-1].lower()
        if any(m in user_msg for m in es_markers):
            es_count += 1
        else:
            en_count += 1
    print(f"\nLanguage distribution:")
    print(f"  Spanish: {es_count} ({es_count/len(all_examples)*100:.1f}%)")
    print(f"  English: {en_count} ({en_count/len(all_examples)*100:.1f}%)")

    # Relation type coverage
    rel_counts = {}
    for ex in all_examples:
        output = json.loads(ex["messages"][2]["content"])
        for rel in output.get("relations", []):
            rt = rel["relation"]
            rel_counts[rt] = rel_counts.get(rt, 0) + 1
    print(f"\nRelation type coverage ({len(rel_counts)}/16):")
    for rt, count in sorted(rel_counts.items(), key=lambda x: -x[1]):
        print(f"  {rt}: {count}")

    # Intent distribution
    intent_counts = {}
    for ex in all_examples:
        output = json.loads(ex["messages"][2]["content"])
        it = output["intent"]["type"]
        intent_counts[it] = intent_counts.get(it, 0) + 1
    print(f"\nIntent distribution:")
    for it, count in sorted(intent_counts.items(), key=lambda x: -x[1]):
        print(f"  {it}: {count} ({count/len(all_examples)*100:.1f}%)")

    # Check for null entity_id
    null_entity_count = 0
    for ex in all_examples:
        output = json.loads(ex["messages"][2]["content"])
        for f in output.get("facts", []):
            if not f.get("entity_id"):
                null_entity_count += 1
    print(f"\nNull/empty entity_id count: {null_entity_count}")

    print(f"\nOutput directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

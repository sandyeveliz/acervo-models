#!/usr/bin/env python3
"""
Generate v3 training data for Acervo S1 model.

Produces ~185 NEW examples across 4 targeted groups:
  G1. Intent bias correction — specific/chat misclassified as overview (~65)
  G2. User-declared facts extraction (~60)
  G3. Multi-entity extraction (~30)
  G4. Gaps not covered by benchmarks (~30)

Usage:
    cd 01_dataset
    python generate_s1_v3_training.py [--seed 42]
"""

import json
import random
import argparse
from pathlib import Path
from copy import deepcopy

from generate_s1_training import (
    PERSONS, PROJECTS, ORGS, FRONTEND, BACKEND, DATABASES, CLOUD, INFRA,
    CSS_FW, LANGUAGES, APP_TYPES_EN, APP_TYPES_ES, JOB_TITLES,
    HP_CHARS, HP_PLACES, LOTR_CHARS, LOTR_PLACES, SW_CHARS, SW_PLACES,
    DUNE_CHARS, DUNE_PLACES, LIT_UNIVERSES,
    FAMILY_RELATIONS, HOBBIES, CITIES, FOODS,
    SUBJECTS, PROFESSORS, ACADEMIC_CONCEPTS,
    _id, node, rel, fact_entry, existing_node, pick, pick_n, pick_hint,
    format_user_input, spanish_chance,
    software_graph, business_graph, literature_graph, personal_graph, academic_graph,
)
from generate_s1_v2_training import make_v2_example, v2_output
from schema import S1_SYSTEM_PROMPT, validate_s1, validate_s1_jsonl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "training_data" / "v3"


# ═══════════════════════════════════════════════════════════════════════════
# Additional pools for v3
# ═══════════════════════════════════════════════════════════════════════════

MODULES_POOL = [
    "Auth Module", "Dashboard", "Notification Service", "Payment Gateway",
    "Search Engine", "Analytics Pipeline", "Admin Panel", "API Gateway",
    "User Management", "File Storage", "Audit Logger", "Report Generator",
    "Scheduler Service", "Email Service", "Cache Layer", "Rate Limiter",
    "Webhook Handler", "Data Importer", "Export Service", "Health Monitor",
]

FEATURES_POOL = [
    "Real-time Notifications", "Role-based Access Control", "CSV Export",
    "Multi-tenant Isolation", "SSO Integration", "Audit Logging",
    "Dark Mode", "Bulk Operations", "Advanced Search", "Two-Factor Auth",
    "Webhook Support", "Custom Dashboards", "API Rate Limiting",
    "Data Encryption at Rest", "Automated Backups", "User Impersonation",
    "Activity Feed", "PDF Report Generation", "GraphQL API", "Localization",
]

PREV_ASSISTANT_POOL = [
    "The project uses {fe} for the frontend and {be} for the backend, with {db} as the database.",
    "{proj} is an internal tool built at {org}. It handles data visualization and reporting.",
    "The codebase is organized as a monorepo with separate frontend and backend packages.",
    "Currently the project has 3 main modules: authentication, dashboard, and reporting.",
    "The team has been working on {proj} for about 6 months. It's in active development.",
    "{proj} uses a microservices architecture with {be} and {db}.",
]

PREV_ASSISTANT_ES_POOL = [
    "El proyecto usa {fe} para el frontend y {be} para el backend, con {db} como base de datos.",
    "{proj} es una herramienta interna construida en {org}. Maneja visualizacion y reportes.",
    "El codebase esta organizado como monorepo con paquetes separados de frontend y backend.",
    "Actualmente el proyecto tiene 3 modulos principales: autenticacion, dashboard y reportes.",
    "El equipo viene trabajando en {proj} hace unos 6 meses. Esta en desarrollo activo.",
]


def _prev_assistant(proj, org, fe, be, db, spanish=False):
    """Generate a plausible previous assistant response."""
    pool = PREV_ASSISTANT_ES_POOL if spanish else PREV_ASSISTANT_POOL
    template = pick(pool)
    return template.format(
        proj=proj[1], org=org[1], fe=fe[1], be=be[1], db=db[1],
    )


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 1 — S1 Intent Bias Correction
# ═══════════════════════════════════════════════════════════════════════════

def gen_g1_specific_corrections():
    """Generate examples correcting specific→overview misclassification."""
    examples = []

    seed_cases = [
        {
            "original": "What database does it use and how is it configured?",
            "variations": [
                "Which database is set up and what's the configuration?",
                "Tell me about the database layer — what's being used?",
                "How is the data store configured in this project?",
            ],
            "variations_es": [
                "Que base de datos usa y como esta configurada?",
            ],
            "trap": "What technologies does this project use?",
        },
        {
            "original": "Let's look at the frontend. What components does it have?",
            "variations": [
                "Show me the frontend components",
                "What's the component structure on the frontend side?",
                "I want to see what UI components exist",
            ],
            "variations_es": [
                "Contame sobre los componentes del frontend",
            ],
            "trap": "Give me an overview of the full architecture",
        },
        {
            "original": "Going back to authentication, what middleware does it use?",
            "variations": [
                "What auth middleware is in place?",
                "How does the authentication layer handle requests?",
                "Tell me about the auth setup specifically",
            ],
            "variations_es": [
                "Volviendo a la autenticacion, que middleware usa?",
            ],
            "trap": "How is the project structured overall?",
        },
        {
            "original": "What issues are currently open?",
            "variations": [
                "Show me the open issues",
                "Are there any unresolved issues I should know about?",
                "Which bugs or tasks are still pending?",
            ],
            "variations_es": [
                "Que issues hay abiertos ahora?",
            ],
            "trap": "What's the overall status of the project?",
        },
        {
            "original": "What's the tech stack for this project?",
            "variations": [
                "What specific technologies are used in the stack?",
                "Break down the tech stack for me",
                "Which frameworks and libraries does this use?",
            ],
            "variations_es": [
                "Que tecnologias especificas tiene el stack?",
            ],
            "trap": "Tell me about this project",
        },
        {
            "original": "What's in the current sprint?",
            "variations": [
                "Show me the sprint backlog",
                "What tasks are assigned in this sprint?",
                "What's being worked on in the current iteration?",
            ],
            "variations_es": [
                "Que hay en el sprint actual?",
            ],
            "trap": "How is the project progressing?",
        },
        {
            "original": "Tell me about the roadmap instead",
            "variations": [
                "Switch to the roadmap — what's planned?",
                "I want to know about the project roadmap",
                "What does the roadmap look like?",
            ],
            "variations_es": [
                "Contame del roadmap mejor",
            ],
            "trap": "Give me a general overview of the project",
        },
        {
            "original": "What progress has been made so far?",
            "variations": [
                "What milestones have been completed?",
                "How far along is the development?",
                "What's been shipped so far?",
            ],
            "variations_es": [
                "Que avances hubo hasta ahora?",
            ],
            "trap": "What is this project about?",
        },
        {
            "original": "Let's look at the architecture decisions",
            "variations": [
                "Show me the ADRs",
                "What architecture decisions were documented?",
                "Walk me through the key technical decisions",
            ],
            "variations_es": [
                "Veamos las decisiones de arquitectura",
            ],
            "trap": "Describe the project for me",
        },
    ]

    for case in seed_cases:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        prev = _prev_assistant(proj, org, fe, be, db)

        # Original — specific
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            prev,
            case["original"],
            v2_output("specific", "with_chunks", action="same"),
        ))

        # 3 variations — specific (pick from EN + ES pool, ensure variety)
        all_vars = list(case["variations"])
        if case.get("variations_es"):
            all_vars.extend(case["variations_es"])
        chosen = random.sample(all_vars, min(3, len(all_vars)))

        for var_msg in chosen:
            nodes2, proj2, org2, fe2, be2, db2, people2 = software_graph("medium")
            topic2 = f"{proj2[1]} development"
            prev2 = _prev_assistant(proj2, org2, fe2, be2, db2)

            # Some variations are topic changes (like "roadmap instead")
            is_topic_change = "instead" in var_msg.lower() or "mejor" in var_msg.lower() or "switch" in var_msg.lower()
            if is_topic_change:
                action, label = "changed", "roadmap"
            else:
                action, label = "same", None

            examples.append(make_v2_example(
                nodes2,
                pick_hint("same" if not is_topic_change else "changed", topic2),
                topic2,
                prev2,
                var_msg,
                v2_output("specific", "with_chunks", action=action, label=label),
            ))

        # 1 trap — overview
        nodes3, proj3, org3, fe3, be3, db3, people3 = software_graph("medium")
        topic3 = f"{proj3[1]} development"
        examples.append(make_v2_example(
            nodes3,
            pick_hint("same", topic3),
            topic3,
            _prev_assistant(proj3, org3, fe3, be3, db3),
            case["trap"],
            v2_output("overview", "summary_only", action="same"),
        ))

    return examples


def gen_g1_chat_corrections():
    """Generate examples correcting chat→overview misclassification."""
    examples = []

    seed_cases = [
        {
            "original": "Interesting, this is a well-structured project",
            "variations": [
                "Nice, the codebase looks really clean",
                "Wow, that's a solid architecture",
                "I like how this is organized",
            ],
            "variations_es": [
                "Interesante, esta bien organizado el proyecto",
            ],
            "trap": "Interesting. Can you give me an overview of all the components?",
        },
        {
            "original": "Ok, I think I understand the project now",
            "variations": [
                "Got it, makes sense",
                "Alright, that clears things up",
                "Ok perfect, I have a good picture now",
            ],
            "variations_es": [
                "Dale, creo que ya entiendo como funciona",
            ],
            "trap": "Ok. Now tell me everything about the deployment setup",
        },
        {
            "original": "These are great detective stories",
            "variations": [
                "Really enjoyable writing style",
                "The characters are well developed",
                "I love this kind of narrative",
            ],
            "variations_es": [
                "Son historias muy buenas",
            ],
            "trap": "Great stories. What other books are in the collection?",
        },
        {
            "original": "Thanks for the overview",
            "variations": [
                "Thanks, that was helpful",
                "Appreciate the explanation",
                "Cool, thanks for walking me through it",
            ],
            "variations_es": [
                "Gracias por el resumen",
            ],
            "trap": "Thanks. Now what else is in the project?",
        },
    ]

    for case in seed_cases:
        # Use either software or literature graph depending on the case
        is_literature = "stories" in case["original"].lower() or "detective" in case["original"].lower()

        if is_literature:
            nodes, chars, places, title, ukey = literature_graph(size="medium")
            topic_label = title
            prev = f"The collection features several stories with characters like {chars[0][1]} and {chars[1][1]}."
        else:
            nodes, proj, org, fe, be, db, people = software_graph("medium")
            topic_label = f"{proj[1]} development"
            prev = _prev_assistant(proj, org, fe, be, db)

        # Original — chat
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            prev,
            case["original"],
            v2_output("chat", "summary_only", action="same"),
        ))

        # 3 variations — chat
        all_vars = list(case["variations"])
        if case.get("variations_es"):
            all_vars.extend(case["variations_es"])
        chosen = random.sample(all_vars, min(3, len(all_vars)))

        for var_msg in chosen:
            if is_literature:
                nodes2, chars2, places2, title2, ukey2 = literature_graph(size="medium")
                topic2 = title2
                prev2 = f"The story follows {chars2[0][1]} on an adventure through {places2[0][1]}."
            else:
                nodes2, proj2, org2, fe2, be2, db2, people2 = software_graph("medium")
                topic2 = f"{proj2[1]} development"
                prev2 = _prev_assistant(proj2, org2, fe2, be2, db2)

            examples.append(make_v2_example(
                nodes2,
                pick_hint("same", topic2),
                topic2,
                prev2,
                var_msg,
                v2_output("chat", "summary_only", action="same"),
            ))

        # 1 trap — overview
        if is_literature:
            nodes3, chars3, places3, title3, ukey3 = literature_graph(size="medium")
            topic3 = title3
            prev3 = f"These are classic tales featuring {chars3[0][1]}."
        else:
            nodes3, proj3, org3, fe3, be3, db3, people3 = software_graph("medium")
            topic3 = f"{proj3[1]} development"
            prev3 = _prev_assistant(proj3, org3, fe3, be3, db3)

        examples.append(make_v2_example(
            nodes3,
            pick_hint("same", topic3),
            topic3,
            prev3,
            case["trap"],
            v2_output("overview", "summary_only", action="same"),
        ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 2 — User-Declared Facts Extraction
# ═══════════════════════════════════════════════════════════════════════════

def gen_g2_people_roles():
    """User declares a person's role in the project."""
    examples = []

    templates_en = [
        ("{person} is handling the {component} module",
         "Handles the {component} module"),
        ("{person} is our new QA lead",
         "New QA lead for the team"),
        ("I put {person} in charge of the backend",
         "In charge of the backend"),
        ("{person} just joined as {role}",
         "Joined the team as {role}"),
        ("{person} is the one who manages deployment",
         "Manages the deployment pipeline"),
    ]

    templates_es = [
        ("{person} es el que maneja el deploy",
         "Maneja el deploy del proyecto"),
        ("Pusimos a {person} a cargo del modulo de {component}",
         "A cargo del modulo de {component}"),
        ("{person} es nuestro nuevo lead de QA",
         "Nuevo lead de QA del equipo"),
        ("{person} recien arranco como {role}",
         "Arranco como {role} en el equipo"),
        ("{person} se encarga de todo lo que es testing",
         "Se encarga del testing del proyecto"),
    ]

    for i, (template, fact_text) in enumerate(templates_en):
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        person = pick(PERSONS)
        component = pick(MODULES_POOL)
        role = pick(JOB_TITLES)
        msg = template.format(person=person[1], component=component, role=role)
        fact = fact_text.format(component=component, role=role)
        topic_label = f"{proj[1]} development"

        ents = []
        rels = []
        # Only add person entity if not already in existing nodes
        if not any(n["id"] == person[0] for n in nodes):
            ents.append(node(person[0], person[1], "person", "PERSONAL"))
        rels.append(rel(person[0], proj[0], "maintains"))

        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            msg,
            v2_output("specific", "summary_only", entities=ents, relations=rels,
                       facts=[fact_entry(person[0], fact)]),
        ))

    for i, (template, fact_text) in enumerate(templates_es):
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        person = pick(PERSONS)
        component = pick(MODULES_POOL)
        role = pick(JOB_TITLES)
        msg = template.format(person=person[1], component=component, role=role)
        fact = fact_text.format(component=component, role=role)
        topic_label = f"{proj[1]} development"

        ents = []
        rels = []
        if not any(n["id"] == person[0] for n in nodes):
            ents.append(node(person[0], person[1], "person", "PERSONAL"))
        rels.append(rel(person[0], proj[0], "maintains"))

        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db, spanish=True),
            msg,
            v2_output("specific", "summary_only", entities=ents, relations=rels,
                       facts=[fact_entry(person[0], fact)]),
        ))

    return examples


def gen_g2_deadlines():
    """User declares deadlines or dates."""
    examples = []

    templates_en = [
        ("We need the MVP ready by end of Q2",
         "MVP deadline is end of Q2"),
        ("The launch date is set for March 15th",
         "Launch date is March 15th"),
        ("We have until Friday to fix the critical bugs",
         "Critical bugs must be fixed by Friday"),
        ("The client wants the demo next Wednesday",
         "Client demo scheduled for next Wednesday"),
        ("Release is planned for the first week of July",
         "Release planned for first week of July"),
    ]

    templates_es = [
        ("Necesitamos esto listo para el viernes",
         "Deadline es el viernes"),
        ("El lanzamiento esta pautado para marzo",
         "Lanzamiento pautado para marzo"),
        ("Tenemos hasta fin de mes para terminar el modulo",
         "Modulo debe estar terminado para fin de mes"),
        ("El cliente quiere la demo la semana que viene",
         "Demo para el cliente la semana que viene"),
        ("La entrega del MVP es para fin de Q2",
         "MVP se entrega a fin de Q2"),
    ]

    for template, fact_text in templates_en:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            template,
            v2_output("specific", "summary_only",
                       facts=[fact_entry(proj[0], fact_text)]),
        ))

    for template, fact_text in templates_es:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db, spanish=True),
            template,
            v2_output("specific", "summary_only",
                       facts=[fact_entry(proj[0], fact_text)]),
        ))

    return examples


def gen_g2_tech_decisions():
    """User declares a technical decision."""
    examples = []

    tech_pairs = [
        (("redis", "Redis"), ("memcached", "Memcached")),
        (("postgresql", "PostgreSQL"), ("mysql", "MySQL")),
        (("vue", "Vue"), ("react", "React")),
        (("fastapi", "FastAPI"), ("django", "Django")),
        (("docker", "Docker"), ("vagrant", "Vagrant")),
    ]

    templates_en = [
        "We decided to use {chosen} instead of {rejected}",
        "After evaluating options, we're going with {chosen} over {rejected}",
        "The team picked {chosen} — {rejected} didn't fit our needs",
        "We switched from {rejected} to {chosen} last week",
        "Going forward we'll use {chosen}, not {rejected}",
    ]

    templates_es = [
        "Decidimos usar {chosen} en lugar de {rejected}",
        "Despues de evaluar, vamos con {chosen} en vez de {rejected}",
        "El equipo eligio {chosen} — {rejected} no nos servia",
        "Cambiamos de {rejected} a {chosen} la semana pasada",
        "De ahora en mas usamos {chosen}, no {rejected}",
    ]

    for i, (chosen_tech, rejected_tech) in enumerate(tech_pairs):
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"

        # EN version
        msg_en = templates_en[i].format(chosen=chosen_tech[1], rejected=rejected_tech[1])
        ents_en = []
        if not any(n["id"] == chosen_tech[0] for n in nodes):
            ents_en.append(node(chosen_tech[0], chosen_tech[1], "technology", "UNIVERSAL"))

        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            msg_en,
            v2_output("specific", "summary_only", entities=ents_en,
                       relations=[rel(proj[0], chosen_tech[0], "uses_technology")],
                       facts=[fact_entry(proj[0], f"Uses {chosen_tech[1]} instead of {rejected_tech[1]}")]),
        ))

        # ES version
        nodes2, proj2, org2, fe2, be2, db2, people2 = software_graph("medium")
        topic2 = f"{proj2[1]} development"
        msg_es = templates_es[i].format(chosen=chosen_tech[1], rejected=rejected_tech[1])
        ents_es = []
        if not any(n["id"] == chosen_tech[0] for n in nodes2):
            ents_es.append(node(chosen_tech[0], chosen_tech[1], "technology", "UNIVERSAL"))

        examples.append(make_v2_example(
            nodes2,
            pick_hint("same", topic2),
            topic2,
            _prev_assistant(proj2, org2, fe2, be2, db2, spanish=True),
            msg_es,
            v2_output("specific", "summary_only", entities=ents_es,
                       relations=[rel(proj2[0], chosen_tech[0], "uses_technology")],
                       facts=[fact_entry(proj2[0], f"Usa {chosen_tech[1]} en lugar de {rejected_tech[1]}")]),
        ))

    return examples


def gen_g2_task_status():
    """User declares task/bug status changes."""
    examples = []

    templates_en = [
        ("I fixed the login bug yesterday",
         "Login bug was fixed"),
        ("The payment integration is done, I finished it this morning",
         "Payment integration is complete"),
        ("I've been working on the search feature all week",
         "Search feature is actively being developed"),
        ("The API migration is about halfway done",
         "API migration is approximately 50% complete"),
        ("I deployed the hotfix to production an hour ago",
         "Hotfix was deployed to production"),
    ]

    templates_es = [
        ("Ya cerre el bug del login ayer",
         "Bug del login fue cerrado"),
        ("La integracion de pagos ya esta lista, la termine esta manana",
         "Integracion de pagos completada"),
        ("Estuve toda la semana con el feature de busqueda",
         "Feature de busqueda en desarrollo activo"),
        ("La migracion del API va por la mitad mas o menos",
         "Migracion del API aproximadamente al 50%"),
        ("Desplegue el hotfix a produccion hace una hora",
         "Hotfix desplegado a produccion"),
    ]

    for template, fact_text in templates_en:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            template,
            v2_output("specific", "summary_only",
                       facts=[fact_entry(proj[0], fact_text)]),
        ))

    for template, fact_text in templates_es:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db, spanish=True),
            template,
            v2_output("specific", "summary_only",
                       facts=[fact_entry(proj[0], fact_text)]),
        ))

    return examples


def gen_g2_corrections():
    """User corrects previously stated information."""
    examples = []

    corrections_en = [
        {
            "msg": "Actually no, the frontend is Vue not React",
            "new_tech": ("vue", "Vue"),
            "old_tech": "React",
            "fact": "Frontend technology is Vue, not React as previously stated",
        },
        {
            "msg": "Wait, I was wrong — the deadline is next month, not this week",
            "new_tech": None,
            "old_tech": None,
            "fact": "Deadline corrected to next month, not this week",
        },
        {
            "msg": "Correction: Alice is the backend lead, not the frontend lead",
            "new_tech": None,
            "old_tech": None,
            "fact": "Alice is the backend lead, not the frontend lead",
        },
        {
            "msg": "I made a mistake earlier, we're on PostgreSQL not MySQL",
            "new_tech": ("postgresql", "PostgreSQL"),
            "old_tech": "MySQL",
            "fact": "Database is PostgreSQL, not MySQL as previously mentioned",
        },
        {
            "msg": "Sorry, let me correct that — the API is built with FastAPI, not Flask",
            "new_tech": ("fastapi", "FastAPI"),
            "old_tech": "Flask",
            "fact": "API framework is FastAPI, not Flask",
        },
    ]

    corrections_es = [
        {
            "msg": "No, me equivoque, no es React sino Vue",
            "new_tech": ("vue", "Vue"),
            "old_tech": "React",
            "fact": "El frontend usa Vue, no React como se dijo antes",
        },
        {
            "msg": "Perdon, me confundi — el deadline es el mes que viene, no esta semana",
            "new_tech": None,
            "old_tech": None,
            "fact": "Deadline corregido al mes que viene, no esta semana",
        },
        {
            "msg": "Correccion: Alice es la lead de backend, no de frontend",
            "new_tech": None,
            "old_tech": None,
            "fact": "Alice es lead de backend, no de frontend",
        },
        {
            "msg": "Me equivoque antes, usamos PostgreSQL, no MySQL",
            "new_tech": ("postgresql", "PostgreSQL"),
            "old_tech": "MySQL",
            "fact": "La base de datos es PostgreSQL, no MySQL",
        },
        {
            "msg": "Perdon, el API esta hecho con FastAPI, no con Flask",
            "new_tech": ("fastapi", "FastAPI"),
            "old_tech": "Flask",
            "fact": "El framework del API es FastAPI, no Flask",
        },
    ]

    for corr in corrections_en:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        ents = []
        rels = []
        if corr["new_tech"]:
            tech = corr["new_tech"]
            if not any(n["id"] == tech[0] for n in nodes):
                ents.append(node(tech[0], tech[1], "technology", "UNIVERSAL"))
            rels.append(rel(proj[0], tech[0], "uses_technology"))

        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            corr["msg"],
            v2_output("specific", "summary_only", entities=ents, relations=rels,
                       facts=[fact_entry(proj[0], corr["fact"])]),
        ))

    for corr in corrections_es:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        ents = []
        rels = []
        if corr["new_tech"]:
            tech = corr["new_tech"]
            if not any(n["id"] == tech[0] for n in nodes):
                ents.append(node(tech[0], tech[1], "technology", "UNIVERSAL"))
            rels.append(rel(proj[0], tech[0], "uses_technology"))

        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db, spanish=True),
            corr["msg"],
            v2_output("specific", "summary_only", entities=ents, relations=rels,
                       facts=[fact_entry(proj[0], corr["fact"])]),
        ))

    return examples


def gen_g2_personal_info():
    """User declares personal information about their involvement."""
    examples = []

    templates_en = [
        ("I wrote that module back in 2024",
         "Wrote this module in 2024"),
        ("I've been the maintainer of this component since day one",
         "Has been maintainer of this component since project inception"),
        ("I set up the CI/CD pipeline myself",
         "Set up the CI/CD pipeline"),
        ("I'm the one who chose this tech stack originally",
         "Originally chose the project's tech stack"),
        ("I onboarded the last three developers to this project",
         "Onboarded the last three developers"),
    ]

    templates_es = [
        ("Yo escribi ese modulo en 2024",
         "Escribio este modulo en 2024"),
        ("Vengo manteniendo este componente desde el dia uno",
         "Mantiene este componente desde el inicio del proyecto"),
        ("Yo arme el pipeline de CI/CD",
         "Armo el pipeline de CI/CD"),
        ("Fui yo el que eligio el stack tecnologico",
         "Eligio el stack tecnologico del proyecto"),
        ("Yo hice el onboarding de los ultimos tres devs",
         "Hizo el onboarding de los ultimos tres desarrolladores"),
    ]

    for template, fact_text in templates_en:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            template,
            v2_output("specific", "summary_only",
                       facts=[fact_entry(proj[0], fact_text)]),
        ))

    for template, fact_text in templates_es:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db, spanish=True),
            template,
            v2_output("specific", "summary_only",
                       facts=[fact_entry(proj[0], fact_text)]),
        ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 3 — Multi-Entity Extraction
# ═══════════════════════════════════════════════════════════════════════════

def gen_g3_literary_scenes():
    """Literary texts with multiple named characters and places."""
    examples = []

    scene_templates = [
        "{c0} and {c1} arrived at {p0}. They found {c2} waiting for them, alongside {c3} who had traveled from {p1}. {c4} appeared shortly after, bringing news.",
        "At {p0}, {c0} confronted {c1} about the betrayal. {c2} tried to mediate while {c3} and {c4} watched from the shadows of {p1}.",
        "The council at {p0} brought together {c0}, {c1}, {c2}, and {c3}. Even {c4} made an appearance, having journeyed from {p1} to attend.",
        "{c0} led the expedition to {p0} with {c1} and {c2}. Along the way they encountered {c3} near {p1}, and later {c4} joined their quest.",
        "In {p0}, {c0} discovered a message from {c1}. {c2} helped decipher it while {c3} kept watch. {c4} arrived from {p1} with reinforcements.",
        "The battle at {p0} was fierce. {c0} fought alongside {c1} and {c2}, while {c3} defended {p1}. {c4} turned the tide with a decisive move.",
    ]

    for i, template in enumerate(scene_templates):
        ukey = pick(list(LIT_UNIVERSES.keys()))
        chars_pool, places_pool, title = LIT_UNIVERSES[ukey]
        chars = pick_n(chars_pool, min(5, len(chars_pool)))
        places = pick_n(places_pool, min(2, len(places_pool)))

        # Build context — only include a few chars/places as existing nodes
        existing_chars = chars[:2]
        existing_places = places[:1]
        nodes = []
        for c in existing_chars:
            nodes.append(existing_node(c[0], c[1], "person", "UNIVERSAL"))
        for p in existing_places:
            nodes.append(existing_node(p[0], p[1], "place", "UNIVERSAL"))

        msg = template.format(
            c0=chars[0][1], c1=chars[1][1], c2=chars[2][1],
            c3=chars[3][1], c4=chars[4][1] if len(chars) > 4 else chars[2][1],
            p0=places[0][1], p1=places[1][1] if len(places) > 1 else places[0][1],
        )

        # Output: ALL named characters and places as entities
        out_entities = []
        for c in chars:
            existing_id = c[0] if any(n["id"] == c[0] for n in nodes) else None
            if existing_id:
                out_entities.append(node(c[0], c[1], "person", "UNIVERSAL", existing_id=existing_id))
            else:
                out_entities.append(node(c[0], c[1], "person", "UNIVERSAL"))
        for p in places:
            existing_id = p[0] if any(n["id"] == p[0] for n in nodes) else None
            if existing_id:
                out_entities.append(node(p[0], p[1], "place", "UNIVERSAL", existing_id=existing_id))
            else:
                out_entities.append(node(p[0], p[1], "place", "UNIVERSAL"))

        examples.append(make_v2_example(
            nodes,
            pick_hint("same", title),
            title,
            f"We're exploring the world of {title}.",
            msg,
            v2_output("specific", "with_chunks", entities=out_entities),
        ))

    return examples


def gen_g3_project_modules():
    """Project descriptions with multiple named modules."""
    examples = []

    for _ in range(6):
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        modules = pick_n(MODULES_POOL, random.randint(4, 6))
        topic_label = f"{proj[1]} development"

        modules_list = ", ".join(modules[:-1]) + f", and {modules[-1]}"
        msg = f"The {proj[1]} project consists of these modules: {modules_list}. Each one is independently deployable."

        out_entities = []
        out_relations = []
        for mod in modules:
            mod_id = _id(mod)
            out_entities.append(node(mod_id, mod, "concept", "PERSONAL"))
            out_relations.append(rel(mod_id, proj[0], "part_of"))

        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            msg,
            v2_output("specific", "with_chunks", entities=out_entities, relations=out_relations),
        ))

    return examples


def gen_g3_team_roster():
    """Documents listing multiple people with roles."""
    examples = []

    for _ in range(6):
        nodes, proj, org, fe, be, db, people_existing = software_graph("small")
        team_size = random.randint(4, 6)
        team = pick_n(PERSONS, team_size)
        roles = pick_n(JOB_TITLES, team_size)

        roster_lines = [f"- {t[1]}: {r}" for t, r in zip(team, roles)]
        msg = f"Here's the current team for {proj[1]}:\n" + "\n".join(roster_lines)

        out_entities = []
        out_relations = []
        for person, role in zip(team, roles):
            existing_id = person[0] if any(n["id"] == person[0] for n in nodes) else None
            if existing_id:
                out_entities.append(node(person[0], person[1], "person", "PERSONAL", existing_id=existing_id))
            else:
                out_entities.append(node(person[0], person[1], "person", "PERSONAL"))
            out_relations.append(rel(person[0], proj[0], "maintains"))

        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            msg,
            v2_output("specific", "with_chunks", entities=out_entities, relations=out_relations),
        ))

    return examples


def gen_g3_prd_features():
    """PRDs with multiple named features."""
    examples = []

    for _ in range(6):
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        features = pick_n(FEATURES_POOL, random.randint(4, 6))
        owner = pick(PERSONS)
        topic_label = f"{proj[1]} development"

        features_list = "\n".join(f"- {f}" for f in features)
        msg = (f"## PRD: {proj[1]} v2.0\n\n"
               f"Features:\n{features_list}\n\n"
               f"Owner: {owner[1]}\nTarget: Q3 2026")

        out_entities = []
        out_relations = []
        for feat in features:
            feat_id = _id(feat)
            out_entities.append(node(feat_id, feat, "concept", "PERSONAL"))
            out_relations.append(rel(feat_id, proj[0], "part_of"))

        # Add owner if not in nodes
        if not any(n["id"] == owner[0] for n in nodes):
            out_entities.append(node(owner[0], owner[1], "person", "PERSONAL"))
        out_relations.append(rel(owner[0], proj[0], "maintains"))

        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            msg,
            v2_output("specific", "with_chunks", entities=out_entities, relations=out_relations),
        ))

    return examples


def gen_g3_changelog():
    """Changelogs with multiple named components and changes."""
    examples = []

    change_templates = [
        ("Added {tech} support", "technology"),
        ("Migrated from {old} to {new}", "technology"),
        ("New {module} module", "concept"),
        ("Upgraded {tech} to latest version", "technology"),
        ("Integrated {tech} for monitoring", "technology"),
    ]

    for _ in range(6):
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"

        num_changes = random.randint(4, 6)
        techs = pick_n(FRONTEND + BACKEND + DATABASES + INFRA + CLOUD, num_changes + 2)
        modules = pick_n(MODULES_POOL, 3)

        changes = []
        out_entities = []
        out_relations = []

        for i in range(num_changes):
            if i < len(techs) - 1 and random.random() < 0.3:
                line = f"- Migrated from {techs[i][1]} to {techs[i+1][1]}"
                for t in [techs[i], techs[i+1]]:
                    if not any(e["id"] == t[0] for e in out_entities) and not any(n["id"] == t[0] for n in nodes):
                        out_entities.append(node(t[0], t[1], "technology", "UNIVERSAL"))
            elif random.random() < 0.4:
                mod = modules[i % len(modules)]
                line = f"- New {mod} module"
                mod_id = _id(mod)
                if not any(e["id"] == mod_id for e in out_entities):
                    out_entities.append(node(mod_id, mod, "concept", "PERSONAL"))
                    out_relations.append(rel(mod_id, proj[0], "part_of"))
            else:
                t = techs[i]
                line = f"- Added {t[1]} support"
                if not any(e["id"] == t[0] for e in out_entities) and not any(n["id"] == t[0] for n in nodes):
                    out_entities.append(node(t[0], t[1], "technology", "UNIVERSAL"))
                    out_relations.append(rel(proj[0], t[0], "uses_technology"))
            changes.append(line)

        msg = f"## Changelog {proj[1]} v3.0\n\n" + "\n".join(changes)

        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            msg,
            v2_output("specific", "with_chunks", entities=out_entities, relations=out_relations),
        ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 4 — Gaps
# ═══════════════════════════════════════════════════════════════════════════

def gen_g4_cross_references():
    """Cross-references to existing entities using different names."""
    examples = []

    cross_ref_en = [
        ("the database", "db", "How is the database performing?"),
        ("the frontend framework", "fe", "Is the frontend framework well documented?"),
        ("the lead dev", "person", "What did the lead dev say about this?"),
        ("that module we discussed", "proj", "Can we revisit that module we discussed?"),
    ]

    cross_ref_es = [
        ("la base de datos", "db", "Como esta andando la base de datos?"),
        ("el framework del frontend", "fe", "Esta bien documentado el framework del frontend?"),
        ("el lead del equipo", "person", "Que dijo el lead del equipo sobre esto?"),
        ("el modulo que vimos recien", "proj", "Podemos volver al modulo que vimos recien?"),
    ]

    for ref_label, ref_type, msg in cross_ref_en:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"

        # Map ref_type to actual existing node
        if ref_type == "db":
            target = db
        elif ref_type == "fe":
            target = fe
        elif ref_type == "person":
            target = people[0] if people else pick(PERSONS)
        else:
            target = proj

        ref_id = _id(ref_label)
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            msg,
            v2_output("specific", "with_chunks",
                       entities=[node(ref_id, ref_label, "concept", "PERSONAL", existing_id=target[0])]),
        ))

    for ref_label, ref_type, msg in cross_ref_es:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"

        if ref_type == "db":
            target = db
        elif ref_type == "fe":
            target = fe
        elif ref_type == "person":
            target = people[0] if people else pick(PERSONS)
        else:
            target = proj

        ref_id = _id(ref_label)
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db, spanish=True),
            msg,
            v2_output("specific", "with_chunks",
                       entities=[node(ref_id, ref_label, "concept", "PERSONAL", existing_id=target[0])]),
        ))

    return examples


def gen_g4_negative_questions():
    """Questions about things that don't exist — should NOT fabricate entities."""
    examples = []

    negative_en = [
        "Does this project have a mobile app?",
        "Are there any end-to-end tests?",
        "Is there an API documentation page?",
        "Do we have a staging environment set up?",
    ]

    negative_es = [
        "Tiene app mobile este proyecto?",
        "Hay tests end-to-end?",
        "Existe alguna pagina de documentacion del API?",
        "Tenemos un ambiente de staging configurado?",
    ]

    for msg in negative_en:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            msg,
            v2_output("specific", "with_chunks"),  # Empty entities — don't fabricate
        ))

    for msg in negative_es:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db, spanish=True),
            msg,
            v2_output("specific", "with_chunks"),
        ))

    return examples


def gen_g4_topic_switches():
    """Explicit topic changes."""
    examples = []

    switch_en = [
        ("Let's move on. Tell me about the payment module", "payment module"),
        ("Forget about that, I want to ask about deployment", "deployment"),
        ("Enough about the frontend. How's the API layer?", "API layer"),
        ("Actually, switch to the testing setup", "testing setup"),
    ]

    switch_es = [
        ("Dejemos eso, hablemos del modulo de pagos", "modulo de pagos"),
        ("Cambiando de tema, como esta el deploy?", "deployment"),
        ("Basta del frontend. Como esta la capa de API?", "capa de API"),
        ("En realidad, pasemos al setup de testing", "testing setup"),
    ]

    for msg, new_topic in switch_en:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        old_topic = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("changed"),
            old_topic,
            _prev_assistant(proj, org, fe, be, db),
            msg,
            v2_output("specific", "with_chunks", action="changed", label=new_topic),
        ))

    for msg, new_topic in switch_es:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        old_topic = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("changed"),
            old_topic,
            _prev_assistant(proj, org, fe, be, db, spanish=True),
            msg,
            v2_output("specific", "with_chunks", action="changed", label=new_topic),
        ))

    return examples


def gen_g4_personal_status():
    """Questions about user's own status/progress."""
    examples = []

    status_en = [
        "What have I worked on this week?",
        "Show me my recent changes",
        "What was the last thing I did on this project?",
    ]

    status_es = [
        "En que estuve trabajando esta semana?",
        "Mostrame mis cambios recientes",
        "Que fue lo ultimo que hice en este proyecto?",
    ]

    for msg in status_en:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db),
            msg,
            v2_output("specific", "with_chunks"),  # Empty — don't invent progress
        ))

    for msg in status_es:
        nodes, proj, org, fe, be, db, people = software_graph("medium")
        topic_label = f"{proj[1]} development"
        examples.append(make_v2_example(
            nodes,
            pick_hint("same", topic_label),
            topic_label,
            _prev_assistant(proj, org, fe, be, db, spanish=True),
            msg,
            v2_output("specific", "with_chunks"),
        ))

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

GROUPS = {
    "v3_g1_s1_intent.jsonl": [
        ("G1: specific→overview correction", gen_g1_specific_corrections),
        ("G1: chat→overview correction", gen_g1_chat_corrections),
    ],
    "v3_g2_s15_recall.jsonl": [
        ("G2: people & roles", gen_g2_people_roles),
        ("G2: deadlines", gen_g2_deadlines),
        ("G2: tech decisions", gen_g2_tech_decisions),
        ("G2: task status", gen_g2_task_status),
        ("G2: corrections", gen_g2_corrections),
        ("G2: personal info", gen_g2_personal_info),
    ],
    "v3_g3_curate_multientity.jsonl": [
        ("G3: literary scenes", gen_g3_literary_scenes),
        ("G3: project modules", gen_g3_project_modules),
        ("G3: team rosters", gen_g3_team_roster),
        ("G3: PRD features", gen_g3_prd_features),
        ("G3: changelogs", gen_g3_changelog),
    ],
    "v3_g4_gaps.jsonl": [
        ("G4: cross-references", gen_g4_cross_references),
        ("G4: negative questions", gen_g4_negative_questions),
        ("G4: topic switches", gen_g4_topic_switches),
        ("G4: personal status", gen_g4_personal_status),
    ],
}


def generate(seed: int = 42):
    """Generate all v3 training data files."""
    random.seed(seed)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_all = 0
    total_valid = 0

    for filename, generators in GROUPS.items():
        filepath = OUTPUT_DIR / filename
        all_examples = []

        for label, gen_fn in generators:
            examples = gen_fn()
            print(f"  {label}: {len(examples)} examples")
            all_examples.extend(examples)

        # Validate each example
        valid = 0
        invalid = 0
        for i, ex in enumerate(all_examples):
            raw = ex["messages"][2]["content"]
            ok, result = validate_s1(raw)
            if ok:
                valid += 1
            else:
                invalid += 1
                print(f"    VALIDATION ERROR in {filename} example {i}: {result}")

        # Write JSONL
        with open(filepath, "w", encoding="utf-8") as f:
            for ex in all_examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        # Intent distribution for this file
        intents = {}
        for ex in all_examples:
            data = json.loads(ex["messages"][2]["content"])
            intent = data.get("intent", "unknown")
            intents[intent] = intents.get(intent, 0) + 1

        print(f"\n  {filename}: {len(all_examples)} total, {valid} valid, {invalid} invalid")
        print(f"  Intent distribution: {intents}")
        print()

        total_all += len(all_examples)
        total_valid += valid

    print(f"{'=' * 60}")
    print(f"TOTAL: {total_all} examples, {total_valid} valid, {total_all - total_valid} invalid")
    print(f"Files written to: {OUTPUT_DIR}")

    # Run jsonl-level validation
    print(f"\n{'=' * 60}")
    print("JSONL-level validation:")
    for filename in GROUPS:
        filepath = OUTPUT_DIR / filename
        stats = validate_s1_jsonl(str(filepath))
        print(f"  {filename}:")
        print(f"    Total: {stats['total']}")
        print(f"    JSON parse rate: {stats['json_parse_rate']:.1%}")
        print(f"    Schema valid rate: {stats['schema_valid_rate']:.1%}")
        if stats["errors"]:
            print(f"    Errors:")
            for line_num, err in stats["errors"]:
                print(f"      Line {line_num}: {err}")


def main():
    parser = argparse.ArgumentParser(description="Generate v3 training data")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    generate(args.seed)


if __name__ == "__main__":
    main()

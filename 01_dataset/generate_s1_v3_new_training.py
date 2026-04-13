#!/usr/bin/env python3
"""
Generate v3-new training data for Acervo S1 model.

Produces ~540 NEW examples across 6 targeted groups:
  G5.  Spanish personal-life facts (200)
  G6.  Spanish personal-life entities + relations (120)
  G7.  Facts on existing entities — GraphFact (100)
  G8.  Missing relation types (30)
  G9.  Intent calibration for personal domains (30)
  G10. Edge cases + robustness (60)

Usage:
    cd 01_dataset
    python generate_s1_v3_new_training.py [--seed 42]
"""

import json
import random
import argparse
from pathlib import Path

from generate_s1_training import (
    PERSONS, PROJECTS, ORGS, FRONTEND, BACKEND, DATABASES,
    _id, node, rel, fact_entry, existing_node, pick, pick_n, pick_hint,
    format_user_input,
)
from schema import S1_SYSTEM_PROMPT, validate_s1, validate_s1_jsonl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "training_data" / "v3_new"


# ═══════════════════════════════════════════════════════════════════════════
# Personal-Life Pools (Spanish/Argentine)
# ═══════════════════════════════════════════════════════════════════════════

AR_PERSONS = [
    ("mariana_lopez", "Mariana López"), ("tomas_vidal", "Tomás Vidal"),
    ("sofia_ruiz", "Sofía Ruiz"), ("agustin_peralta", "Agustín Peralta"),
    ("valentina_gomez", "Valentina Gómez"), ("facundo_herrera", "Facundo Herrera"),
    ("camila_torres", "Camila Torres"), ("joaquin_navarro", "Joaquín Navarro"),
    ("lucia_mendez", "Lucía Méndez"), ("mateo_rios", "Mateo Ríos"),
    ("renata_castro", "Renata Castro"), ("bruno_acosta", "Bruno Acosta"),
    ("elena_molina", "Elena Molina"), ("ramiro_gimenez", "Ramiro Giménez"),
    ("celeste_quiroga", "Celeste Quiroga"), ("german_luna", "Germán Luna"),
    ("ailen_diaz", "Ailén Díaz"), ("francisco_leiva", "Francisco Leiva"),
    ("rocio_sosa", "Rocío Sosa"), ("nicolas_aguirre", "Nicolás Aguirre"),
    ("pilar_romero", "Pilar Romero"), ("ignacio_ibarra", "Ignacio Ibarra"),
    ("florencia_paz", "Florencia Paz"), ("santiago_moreno", "Santiago Moreno"),
]

AR_CITIES = [
    ("mendoza", "Mendoza"), ("cordoba", "Córdoba"), ("rosario", "Rosario"),
    ("bahia_blanca", "Bahía Blanca"), ("mar_del_plata", "Mar del Plata"),
    ("salta", "Salta"), ("san_martin_andes", "San Martín de los Andes"),
    ("bariloche", "Bariloche"), ("ushuaia", "Ushuaia"), ("tucuman", "Tucumán"),
    ("neuquen", "Neuquén"), ("la_plata", "La Plata"), ("parana", "Paraná"),
    ("san_juan", "San Juan"), ("san_rafael", "San Rafael"),
]

AR_BARRIOS = [
    ("villa_crespo", "Villa Crespo"), ("palermo", "Palermo"),
    ("belgrano", "Belgrano"), ("guemes", "Güemes"),
    ("fisherton", "Fisherton"), ("alta_cordoba", "Alta Córdoba"),
    ("chacras_coria", "Chacras de Coria"), ("cerro_gloria", "Cerro de la Gloria"),
    ("centro", "Centro"), ("la_florida", "La Florida"),
    ("alberdi", "Alberdi"), ("nueva_cordoba", "Nueva Córdoba"),
    ("barrio_norte", "Barrio Norte"), ("villa_urquiza", "Villa Urquiza"),
]

AR_BUSINESSES = [
    ("corralon_sauce", "Corralón El Sauce", "organization"),
    ("inmobiliaria_lagos", "Inmobiliaria Lagos", "organization"),
    ("metalurgica_andes", "Metalúrgica Andes", "organization"),
    ("clinica_san_lucas", "Clínica San Lucas", "organization"),
    ("construir_patagonia", "Construir Patagonia SRL", "organization"),
    ("estudio_vidal", "Estudio Vidal Arquitectos", "organization"),
    ("gimnasio_power", "Gimnasio Power", "organization"),
    ("marmoleria_centro", "Marmolería Centro", "organization"),
    ("electricidad_sur", "Electricidad del Sur", "organization"),
    ("vinoteca_andes", "Vinoteca Los Andes", "organization"),
    ("veterinaria_amigos", "Veterinaria Amigos", "organization"),
    ("agencia_viajes_sol", "Agencia de Viajes Sol", "organization"),
    ("farmacia_nueva", "Farmacia Nueva", "organization"),
    ("panaderia_artesanal", "Panadería Artesanal", "organization"),
]

# Financial instruments
FIN_INSTRUMENTS = [
    ("fondo_conservador", "Fondo Conservador", "concept"),
    ("fondo_crecimiento", "Fondo Crecimiento", "concept"),
    ("fondo_vacaciones", "Fondo Vacaciones", "concept"),
    ("fondo_educacion", "Fondo Educación", "concept"),
    ("fondo_retiro", "Fondo Retiro", "concept"),
    ("plazo_fijo", "Plazo Fijo", "concept"),
    ("fci_money_market", "FCI Money Market", "concept"),
    ("cedear_apple", "AAPL (CEDEAR)", "concept"),
    ("cedear_google", "GOOGL (CEDEAR)", "concept"),
    ("cedear_mercadolibre", "MELI (CEDEAR)", "concept"),
    ("bono_cer", "Bono CER TX26", "concept"),
    ("dolar_mep", "Dólar MEP", "concept"),
    ("cripto_btc", "Bitcoin", "technology"),
    ("cripto_eth", "Ethereum", "technology"),
]

# Medical/health
MEDICAL = [
    ("pediatra", "Pediatra", "concept"),
    ("ginecologa", "Ginecóloga", "concept"),
    ("kinesiologo", "Kinesiólogo", "concept"),
    ("nutricionista", "Nutricionista", "concept"),
    ("traumatologo", "Traumatólogo", "concept"),
    ("odontologo", "Odontólogo", "concept"),
]

TRAVEL_DESTINATIONS = [
    ("madrid", "Madrid"), ("barcelona_es", "Barcelona"),
    ("roma", "Roma"), ("paris", "París"),
    ("lisboa", "Lisboa"), ("amsterdam", "Ámsterdam"),
    ("londres", "Londres"), ("berlin", "Berlín"),
    ("florencia", "Florencia"), ("praga", "Praga"),
]

TRAVEL_BARRIOS = [
    ("malasana", "Malasaña"), ("chueca", "Chueca"),
    ("eixample", "Eixample"), ("born", "El Born"),
    ("trastevere", "Trastevere"), ("monti", "Monti"),
    ("montmartre", "Montmartre"), ("marais", "Le Marais"),
]

TRAVEL_ATTRACTIONS = [
    ("museo_prado", "Museo del Prado"), ("sagrada_familia", "Sagrada Familia"),
    ("coliseo", "Coliseo Romano"), ("torre_eiffel", "Torre Eiffel"),
    ("alhambra", "La Alhambra"), ("park_guell", "Park Güell"),
    ("vaticano", "El Vaticano"), ("ponte_vecchio", "Ponte Vecchio"),
]

FITNESS_ACTIVITIES = [
    ("running", "Running"), ("crossfit", "CrossFit"),
    ("natacion", "Natación"), ("ciclismo", "Ciclismo"),
    ("yoga", "Yoga"), ("funcional", "Entrenamiento Funcional"),
    ("trail_running", "Trail Running"), ("musculacion", "Musculación"),
]

# Software tech for Spanish context
TECH_ES = [
    ("nodejs", "Node.js"), ("pnpm", "pnpm"), ("bcrypt", "bcrypt"),
    ("jwt", "JWT"), ("zod", "Zod"), ("zustand", "Zustand"),
    ("tailwind", "Tailwind CSS"), ("axios", "Axios"),
    ("vitest", "Vitest"), ("prisma", "Prisma"),
    ("supabase", "Supabase"), ("vercel", "Vercel"),
    ("github_actions", "GitHub Actions"), ("recharts", "Recharts"),
    ("swagger", "Swagger/OpenAPI"), ("tesseract_js", "Tesseract.js"),
]

PROJECTS_ES = [
    ("dividiapp", "DividiApp"), ("checkear", "Checkear"),
    ("walletfy", "Walletfy"), ("gastosya", "GastosYa"),
    ("turnero", "Turnero"), ("stockapp", "StockApp"),
    ("fittrack", "FitTrack"), ("viajemos", "Viajemos"),
]


# ═══════════════════════════════════════════════════════════════════════════
# Graph State Generators
# ═══════════════════════════════════════════════════════════════════════════

def personal_finance_graph():
    """Graph state for personal finance scenario."""
    person = pick(AR_PERSONS)
    city = pick(AR_CITIES)
    funds = pick_n(FIN_INSTRUMENTS[:6], random.randint(2, 4))
    nodes = [
        existing_node(person[0], person[1], "person", "PERSONAL"),
        existing_node(city[0], city[1], "place", "UNIVERSAL"),
    ]
    for f in funds:
        nodes.append(existing_node(f[0], f[1], f[2], "PERSONAL"))
    return nodes, person, city, funds


def real_estate_graph():
    """Graph state for real estate / construction scenario."""
    person = pick(AR_PERSONS)
    city = pick(AR_CITIES)
    barrio = pick(AR_BARRIOS)
    architect = pick([p for p in AR_PERSONS if p != person])
    builder = pick(AR_BUSINESSES[:6])
    nodes = [
        existing_node(person[0], person[1], "person", "PERSONAL"),
        existing_node(city[0], city[1], "place", "UNIVERSAL"),
        existing_node(barrio[0], barrio[1], "place", "PERSONAL"),
        existing_node(architect[0], architect[1], "person", "PERSONAL"),
        existing_node(builder[0], builder[1], "organization", "PERSONAL"),
    ]
    return nodes, person, city, barrio, architect, builder


def health_family_graph():
    """Graph state for health / family scenario."""
    parent = pick(AR_PERSONS)
    partner = pick([p for p in AR_PERSONS if p != parent])
    child_name = pick(["Emilia", "Bautista", "Olivia", "Lautaro", "Emma", "Thiago"])
    child_id = _id(child_name)
    clinic = pick([b for b in AR_BUSINESSES if "clinica" in b[0].lower() or "veterinaria" not in b[0].lower()][:3])
    city = pick(AR_CITIES)
    nodes = [
        existing_node(parent[0], parent[1], "person", "PERSONAL"),
        existing_node(partner[0], partner[1], "person", "PERSONAL"),
        existing_node(child_id, child_name, "person", "PERSONAL"),
        existing_node(city[0], city[1], "place", "UNIVERSAL"),
    ]
    return nodes, parent, partner, (child_id, child_name), city, clinic


def travel_graph():
    """Graph state for travel planning scenario."""
    person = pick(AR_PERSONS)
    dest = pick(TRAVEL_DESTINATIONS)
    city_origin = pick(AR_CITIES)
    trip_id = f"viaje_{dest[0]}"
    nodes = [
        existing_node(person[0], person[1], "person", "PERSONAL"),
        existing_node(city_origin[0], city_origin[1], "place", "UNIVERSAL"),
        existing_node(dest[0], dest[1], "place", "UNIVERSAL"),
        existing_node(trip_id, f"Viaje a {dest[1]}", "event", "PERSONAL"),
    ]
    return nodes, person, city_origin, dest, trip_id


def fitness_graph():
    """Graph state for fitness / sports scenario."""
    person = pick(AR_PERSONS)
    activity = pick(FITNESS_ACTIVITIES)
    trainer = pick([p for p in AR_PERSONS if p != person])
    gym = pick([b for b in AR_BUSINESSES if "gimnasio" in b[0].lower() or "power" in b[0].lower()])
    city = pick(AR_CITIES)
    nodes = [
        existing_node(person[0], person[1], "person", "PERSONAL"),
        existing_node(_id(activity[1]), activity[1], "concept", "PERSONAL"),
        existing_node(city[0], city[1], "place", "UNIVERSAL"),
    ]
    return nodes, person, activity, trainer, gym, city


def freelance_graph():
    """Graph state for work / freelance scenario."""
    person = pick(AR_PERSONS)
    project = pick(PROJECTS_ES)
    client = pick(AR_BUSINESSES)
    city = pick(AR_CITIES)
    tech = pick_n(TECH_ES, random.randint(2, 3))
    nodes = [
        existing_node(person[0], person[1], "person", "PERSONAL"),
        existing_node(project[0], project[1], "project", "PERSONAL"),
        existing_node(client[0], client[1], "organization", "PERSONAL"),
        existing_node(city[0], city[1], "place", "UNIVERSAL"),
    ]
    for t in tech:
        nodes.append(existing_node(t[0], t[1], "technology", "UNIVERSAL"))
    return nodes, person, project, client, city, tech


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def make_example(existing_nodes, topic_hint, current_topic, prev_assistant, user_msg, output):
    """Build a training example with the updated system prompt."""
    return {
        "messages": [
            {"role": "system", "content": S1_SYSTEM_PROMPT},
            {"role": "user", "content": format_user_input(
                existing_nodes, topic_hint, current_topic, prev_assistant, user_msg
            )},
            {"role": "assistant", "content": json.dumps(output, ensure_ascii=False)},
        ]
    }


def out(intent, retrieval, action="same", label=None, entities=None, relations=None, facts=None):
    """Build an output dict."""
    topic = {"action": action, "label": label}
    return {
        "intent": intent,
        "topic": topic,
        "retrieval": retrieval,
        "entities": entities or [],
        "relations": relations or [],
        "facts": facts or [],
    }


def _amount():
    """Random peso/dollar amount."""
    return pick([
        "150.000 ARS", "500.000 ARS", "1.200.000 ARS", "2.500.000 ARS",
        "4.000.000 ARS", "350.000 ARS", "780.000 ARS", "3.100.000 ARS",
        "5.500 USD", "12.000 USD", "25.000 USD", "45.000 USD",
        "78.000 USD", "120.000 USD", "180.000 USD", "3.200 USD",
    ])


def _percent():
    return pick(["5%", "8%", "12%", "15%", "22%", "30%", "35%", "40%", "55%", "75%"])


def _months():
    return pick(["3 meses", "6 meses", "8 meses", "12 meses", "18 meses", "24 meses"])


def _prev_es(project_label):
    templates = [
        f"El proyecto {project_label} está en desarrollo activo.",
        f"Estuvimos viendo los avances de {project_label}.",
        f"Te cuento las novedades sobre {project_label}.",
        f"{project_label} viene avanzando bien estas semanas.",
    ]
    return pick(templates)


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 5 — Spanish Personal-Life Facts (200 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g5a_casa():
    """G5a: Casa/Construcción facts (35 examples)."""
    examples = []
    templates = [
        ("El terreno costó {amt}. Son {n}m2 en {barrio}.",
         [("Terreno costó {amt}, {n}m2", "user")]),
        ("El presupuesto de la obra llave en mano es {amt}.",
         [("Presupuesto llave en mano: {amt}", "user")]),
        ("Empezamos los cimientos la semana pasada. El hormigón lo trajo {biz}.",
         [("Cimientos iniciados", "user")]),
        ("Los pisos van porcelanato símil madera en living y cerámico en baños. Presupuesto pisos: {amt}.",
         [("Pisos: porcelanato living, cerámico baños. Presupuesto: {amt}", "user")]),
        ("La estructura de hormigón ya está terminada. Costó {amt} con mano de obra incluida.",
         [("Estructura hormigón terminada, costo: {amt}", "user")]),
        ("El arquitecto {arq} nos pasó un presupuesto actualizado: {amt} total.",
         [("Presupuesto actualizado por {arq}: {amt}", "user")]),
        ("Compramos las aberturas de aluminio. Ventanas + puerta principal: {amt}.",
         [("Aberturas aluminio: {amt}", "user")]),
        ("El crédito hipotecario fue aprobado: {amt} en UVA a 20 años. Cuota inicial: {cuota}/mes.",
         [("Crédito aprobado: {amt} UVA 20 años, cuota {cuota}/mes", "user")]),
        ("Instalación eléctrica completa: {amt}. Incluye tablero, bocas y mano de obra.",
         [("Instalación eléctrica: {amt} con tablero y mano de obra", "user")]),
        ("El gas lo aprobó {empresa}. Matrícula habilitante en trámite, {n} días hábiles.",
         [("Gas aprobado por {empresa}, matrícula en trámite", "user")]),
        ("Pintura interior y exterior: {amt}. El pintor arranca la semana que viene.",
         [("Pintura total: {amt}", "user")]),
        ("Mes {m} de la obra: gastados {gastado} de {total} presupuestados ({pct}).",
         [("Mes {m}: gastados {gastado} de {total} ({pct})", "user")]),
    ]
    for _ in range(35):
        graph_data = real_estate_graph()
        nodes, person, city, barrio, architect, builder = graph_data
        tmpl = pick(templates)
        msg_tmpl, fact_tmpls = tmpl
        n = random.randint(200, 800)
        m = random.randint(1, 12)
        amt = _amount()
        cuota = pick(["320.000 ARS", "450.000 ARS", "580.000 ARS", "720.000 ARS"])
        gastado = pick(["45.000 USD", "72.000 USD", "95.000 USD", "130.000 USD", "175.000 USD"])
        total = pick(["150.000 USD", "180.000 USD", "220.000 USD", "250.000 USD"])
        pct = pick(["30%", "40%", "53%", "60%", "72%", "85%"])
        empresa = pick(["Camuzzi", "MetroGas", "Ecogas", "Litoral Gas"])
        replacements = {
            "amt": amt, "n": str(n), "barrio": barrio[1], "biz": builder[1],
            "arq": architect[1], "cuota": cuota, "empresa": empresa,
            "m": str(m), "gastado": gastado, "total": total, "pct": pct,
        }
        user_msg = msg_tmpl.format(**replacements)
        facts_list = [
            fact_entry(pick([person[0], barrio[0], builder[0]]),
                       ft[0].format(**replacements), ft[1])
            for ft in fact_tmpls
        ]
        output = out("specific", "summary_only", facts=facts_list)
        hint = pick_hint("same", f"Proyecto casa en {barrio[1]}")
        ex = make_example(nodes, hint, f"Proyecto casa en {barrio[1]}",
                          _prev_es(f"la casa en {barrio[1]}"), user_msg, output)
        examples.append(ex)
    return examples


def gen_g5b_finanzas():
    """G5b: Finanzas personales facts (35 examples)."""
    examples = []
    templates = [
        ("Mi sueldo neto es {amt} por mes. Soy {cat}.",
         [("Sueldo neto: {amt}/mes, {cat}", "user")]),
        ("El fondo de {fondo} ya tiene {amt} acumulados.",
         [("Saldo acumulado: {amt}", "user")]),
        ("Compré {n} CEDEARs de {ticker} a {precio} cada uno.",
         [("Compra {n} CEDEARs {ticker} a {precio} c/u", "user")]),
        ("El plazo fijo rinde {tna} TNA. Vence en {dias} días.",
         [("Plazo fijo: {tna} TNA, vence en {dias} días", "user")]),
        ("Distribución mensual: {pct1} ahorro, {pct2} gastos fijos, {pct3} variable.",
         [("Distribución: {pct1} ahorro, {pct2} fijos, {pct3} variable", "user")]),
        ("El alquiler subió a {amt} desde este mes. El año pasado pagaba {amt2}.",
         [("Alquiler actual: {amt}, anterior: {amt2}", "user")]),
        ("Invertí {amt} en dólar MEP a {cotiz} pesos. Ahora cotiza {cotiz2}.",
         [("Dólar MEP: compra a {cotiz}, actual {cotiz2}", "user")]),
        ("La tarjeta de crédito cierra el 15 y vence el 5. Límite: {amt}.",
         [("TC: cierre 15, vencimiento 5, límite {amt}", "user")]),
        ("Gastos del mes: {amt} en supermercado, {amt2} en servicios, {amt3} en transporte.",
         [("Gastos mes: super {amt}, servicios {amt2}, transporte {amt3}", "user")]),
        ("Vendí {n} bonos {ticker} a {precio}. Ganancia: {pct} en {meses}.",
         [("Venta {n} {ticker} a {precio}, ganancia {pct} en {meses}", "user")]),
    ]
    for _ in range(35):
        nodes, person, city, funds = personal_finance_graph()
        tmpl = pick(templates)
        msg_tmpl, fact_tmpls = tmpl
        fund = pick(funds) if funds else pick(FIN_INSTRUMENTS[:6])
        ticker = pick(["AAPL", "GOOGL", "MELI", "AMZN", "MSFT", "TSLA"])
        tna = pick(["45%", "55%", "65%", "75%", "82%", "90%"])
        dias = random.randint(30, 365)
        n = random.randint(1, 50)
        precio = pick(["45.200 ARS", "78.500 ARS", "125.000 ARS", "15.600 ARS"])
        cotiz = pick(["1.050", "1.120", "1.180", "1.250"])
        cotiz2 = pick(["1.150", "1.200", "1.280", "1.350"])
        cat = pick(["monotributista", "relación de dependencia", "autónomo"])
        meses = pick(["3 meses", "6 meses", "1 año"])
        pct1 = pick(["30%", "40%", "25%", "35%"])
        pct2 = pick(["40%", "35%", "45%", "50%"])
        pct3 = pick(["30%", "25%", "20%", "15%"])
        replacements = {
            "amt": _amount(), "amt2": _amount(), "amt3": _amount(),
            "fondo": fund[1], "ticker": ticker, "tna": tna, "dias": str(dias),
            "n": str(n), "precio": precio, "cotiz": cotiz, "cotiz2": cotiz2,
            "cat": cat, "meses": meses, "pct": _percent(),
            "pct1": pct1, "pct2": pct2, "pct3": pct3,
        }
        user_msg = msg_tmpl.format(**replacements)
        facts_list = [
            fact_entry(fund[0], ft[0].format(**replacements), ft[1])
            for ft in fact_tmpls
        ]
        output = out("specific", "summary_only", facts=facts_list)
        hint = pick_hint("same", "Finanzas personales")
        ex = make_example(nodes, hint, "Finanzas personales",
                          _prev_es("las finanzas"), user_msg, output)
        examples.append(ex)
    return examples


def gen_g5c_salud():
    """G5c: Salud/Familia facts (30 examples)."""
    examples = []
    templates = [
        ("Llevé a {child} al pediatra. Pesó {peso}kg y midió {talla}cm. Todo normal.",
         [("Peso: {peso}kg, talla: {talla}cm. Control normal", "user")]),
        ("Turno con la ginecóloga el {dia}. Control de rutina, todo bien.",
         [("Control ginecológico {dia}: normal", "user")]),
        ("Empezamos con BLW para {child}. Primer alimento: banana y palta.",
         [("Inicio BLW: banana y palta", "user")]),
        ("{child} ya camina solo/a desde la semana pasada. Tiene {meses} meses.",
         [("Camina solo/a desde los {meses} meses", "user")]),
        ("Vacuna de {child}: {vacuna}. Próxima dosis en {n} meses.",
         [("Vacuna {vacuna} aplicada, próxima en {n} meses", "user")]),
        ("La obra social cubre {pct} del tratamiento. El resto sale {amt}.",
         [("Cobertura obra social: {pct}, copago: {amt}", "user")]),
        ("{partner} empezó kinesiología por la espalda. {n} sesiones por semana.",
         [("Kinesiología: {n} sesiones/semana por dolor de espalda", "user")]),
        ("Turno odontólogo para {child}: primera visita dental. Sin caries.",
         [("Primera visita dental: sin caries", "user")]),
        ("El pediatra recetó {med} para {child}. Dosis: {dosis} cada {horas} horas.",
         [("Receta: {med}, dosis {dosis} cada {horas}hs", "user")]),
    ]
    for _ in range(30):
        graph_data = health_family_graph()
        nodes, parent, partner, child, city, clinic = graph_data
        tmpl = pick(templates)
        msg_tmpl, fact_tmpls = tmpl
        peso = round(random.uniform(3.5, 14.0), 1)
        talla = random.randint(48, 85)
        meses = random.randint(6, 24)
        dia = pick(["viernes", "lunes", "martes", "miércoles", "jueves"])
        vacuna = pick(["triple viral", "antigripal", "hepatitis B", "neumococo", "rotavirus"])
        n = random.randint(1, 4)
        med = pick(["ibuprofeno", "amoxicilina", "paracetamol", "salbutamol"])
        dosis = pick(["2.5ml", "5ml", "1 comprimido", "15 gotas"])
        horas = pick(["6", "8", "12"])
        replacements = {
            "child": child[1], "partner": partner[1], "peso": str(peso),
            "talla": str(talla), "meses": str(meses), "dia": dia,
            "vacuna": vacuna, "n": str(n), "amt": _amount(), "pct": _percent(),
            "med": med, "dosis": dosis, "horas": horas,
        }
        user_msg = msg_tmpl.format(**replacements)
        facts_list = [
            fact_entry(child[0], ft[0].format(**replacements), ft[1])
            for ft in fact_tmpls
        ]
        output = out("specific", "summary_only", facts=facts_list)
        hint = pick_hint("same", f"Salud de {child[1]}")
        ex = make_example(nodes, hint, f"Salud de {child[1]}",
                          _prev_es(f"la salud de {child[1]}"), user_msg, output)
        examples.append(ex)
    return examples


def gen_g5d_viajes():
    """G5d: Viajes facts (25 examples)."""
    examples = []
    templates = [
        ("Los vuelos a {dest} nos salen {amt} por persona, ida y vuelta.",
         [("Vuelos a {dest}: {amt}/persona ida y vuelta", "user")]),
        ("Reservamos hotel en {barrio} por {n} noches. Total: {amt}.",
         [("Hotel en {barrio}: {n} noches, {amt} total", "user")]),
        ("El seguro de viaje cuesta {amt} para {n} días. Cobertura médica hasta 50.000 USD.",
         [("Seguro viaje: {amt}, {n} días, cobertura 50K USD", "user")]),
        ("Presupuesto total del viaje: {amt}. Vuelos {pct1}, alojamiento {pct2}, gastos diarios {pct3}.",
         [("Presupuesto viaje: {amt}. Vuelos {pct1}, hotel {pct2}, diarios {pct3}", "user")]),
        ("Tengo ciudadanía {nac}. No necesito visa para {dest}.",
         [("Tiene ciudadanía {nac}, sin visa para {dest}", "user")]),
        ("El itinerario: {n1} días en {dest1} + {n2} días en {dest2}.",
         [("Itinerario: {n1}d {dest1} + {n2}d {dest2}", "user")]),
        ("Sacamos las entradas para {atraccion}: {amt} por persona.",
         [("Entradas {atraccion}: {amt}/persona", "user")]),
        ("El Airbnb en {barrio} sale {amt} por noche. Tiene cocina y lavarropas.",
         [("Airbnb {barrio}: {amt}/noche con cocina", "user")]),
    ]
    for _ in range(25):
        graph_data = travel_graph()
        nodes, person, city_origin, dest, trip_id = graph_data
        tmpl = pick(templates)
        msg_tmpl, fact_tmpls = tmpl
        barrio = pick(TRAVEL_BARRIOS)
        atraccion = pick(TRAVEL_ATTRACTIONS)
        dest2 = pick([d for d in TRAVEL_DESTINATIONS if d != dest])
        n = random.randint(3, 21)
        n1 = random.randint(3, 10)
        n2 = random.randint(3, 10)
        nac = pick(["italiana", "española", "argentina", "uruguaya"])
        pct1 = pick(["35%", "40%", "45%"])
        pct2 = pick(["30%", "35%", "40%"])
        pct3 = pick(["20%", "25%", "30%"])
        replacements = {
            "dest": dest[1], "dest1": dest[1], "dest2": dest2[1],
            "barrio": barrio[1], "atraccion": atraccion[1],
            "amt": _amount(), "n": str(n), "n1": str(n1), "n2": str(n2),
            "nac": nac, "pct1": pct1, "pct2": pct2, "pct3": pct3,
        }
        user_msg = msg_tmpl.format(**replacements)
        facts_list = [
            fact_entry(trip_id, ft[0].format(**replacements), ft[1])
            for ft in fact_tmpls
        ]
        output = out("specific", "summary_only", facts=facts_list)
        hint = pick_hint("same", f"Viaje a {dest[1]}")
        ex = make_example(nodes, hint, f"Viaje a {dest[1]}",
                          _prev_es(f"el viaje a {dest[1]}"), user_msg, output)
        examples.append(ex)
    return examples


def gen_g5e_fitness():
    """G5e: Fitness facts (25 examples)."""
    examples = []
    templates = [
        ("Corrí {dist}km en {tiempo}. Mejor marca personal.",
         [("{dist}km en {tiempo}, marca personal", "user")]),
        ("Hoy entrené {actividad}. Hice {series} series de {reps} repeticiones.",
         [("Entreno {actividad}: {series}x{reps}", "user")]),
        ("Mi peso actual es {peso}kg. Objetivo: {obj}kg para {cuando}.",
         [("Peso: {peso}kg, objetivo {obj}kg para {cuando}", "user")]),
        ("Carrera de {dist}km el {fecha}. Inscripción: {amt}.",
         [("Carrera {dist}km {fecha}, inscripción {amt}", "user")]),
        ("El entrenador {trainer} me armó un plan de {n} días por semana.",
         [("Plan de entrenamiento: {n} días/semana por {trainer}", "user")]),
        ("Récord en press de banca: {peso_rec}kg. El anterior era {peso_ant}kg.",
         [("Press banca récord: {peso_rec}kg (anterior {peso_ant}kg)", "user")]),
        ("Semana de descarga: volumen al {pct} para recuperar.",
         [("Semana descarga: volumen al {pct}", "user")]),
        ("Nutrición pre-carrera: carbo loading {n} días antes. Día de carrera: banana + gel.",
         [("Pre-carrera: carbo loading {n}d, banana + gel", "user")]),
    ]
    for _ in range(25):
        graph_data = fitness_graph()
        nodes, person, activity, trainer, gym, city = graph_data
        tmpl = pick(templates)
        msg_tmpl, fact_tmpls = tmpl
        dist = pick(["3", "5", "10", "15", "21"])
        tiempo = pick(["14:20", "22:45", "27:30", "32:15", "48:50", "1:05:30", "1:32:00"])
        peso = round(random.uniform(55.0, 100.0), 1)
        obj = round(peso + random.uniform(-10, 10), 1)
        cuando = pick(["junio", "agosto", "diciembre", "marzo", "fin de año"])
        series = random.randint(3, 5)
        reps = pick(["8", "10", "12", "15"])
        fecha = pick(["15 de mayo", "3 de agosto", "20 de octubre", "12 de noviembre"])
        peso_rec = random.randint(40, 140)
        peso_ant = peso_rec - random.randint(2, 10)
        n = random.randint(3, 6)
        pct = pick(["50%", "60%", "70%"])
        replacements = {
            "dist": dist, "tiempo": tiempo, "peso": str(peso), "obj": str(obj),
            "cuando": cuando, "actividad": activity[1], "trainer": trainer[1],
            "series": str(series), "reps": reps, "fecha": fecha,
            "peso_rec": str(peso_rec), "peso_ant": str(peso_ant),
            "n": str(n), "pct": pct, "amt": _amount(),
        }
        user_msg = msg_tmpl.format(**replacements)
        facts_list = [
            fact_entry(person[0], ft[0].format(**replacements), ft[1])
            for ft in fact_tmpls
        ]
        output = out("specific", "summary_only", facts=facts_list)
        hint = pick_hint("same", activity[1])
        ex = make_example(nodes, hint, activity[1],
                          _prev_es(activity[1]), user_msg, output)
        examples.append(ex)
    return examples


def gen_g5f_trabajo():
    """G5f: Trabajo/Freelance facts (25 examples)."""
    examples = []
    templates = [
        ("Facturé {amt} en {mes}. El cliente {client} pagó al día.",
         [("Facturación {mes}: {amt}. {client} pagó en tiempo", "user")]),
        ("Me aumentaron el sueldo a {amt} brutos. Neto queda aprox {neto}.",
         [("Aumento sueldo: {amt} brutos, ~{neto} neto", "user")]),
        ("Sprint terminado: {n} tareas completadas de {total}. Velocidad: {vel} puntos.",
         [("Sprint: {n}/{total} tareas, velocidad {vel} pts", "user")]),
        ("Deploy a producción de {feature}. Sin incidentes por ahora.",
         [("Deploy {feature} a producción, sin incidentes", "user")]),
        ("Reunión con {client}: quieren el MVP para {fecha}. Presupuesto: {amt}.",
         [("MVP para {client}: deadline {fecha}, presupuesto {amt}", "user")]),
        ("Contratamos a {new_hire} como {rol}. Arranca el {fecha}.",
         [("{new_hire} contratado/a como {rol}, inicio {fecha}", "user")]),
        ("El proyecto lleva {n} meses de desarrollo. {pct} completado.",
         [("{n} meses desarrollo, {pct} completado", "user")]),
        ("Pagué monotributo categoría {cat}. Son {amt} por mes.",
         [("Monotributo cat {cat}: {amt}/mes", "user")]),
    ]
    for _ in range(25):
        graph_data = freelance_graph()
        nodes, person, project, client, city, tech = graph_data
        tmpl = pick(templates)
        msg_tmpl, fact_tmpls = tmpl
        new_hire = pick(AR_PERSONS)
        mes = pick(["enero", "febrero", "marzo", "abril", "mayo", "junio",
                     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"])
        neto = _amount()
        n = random.randint(1, 18)
        total = random.randint(8, 25)
        vel = random.randint(15, 60)
        feature = pick(["auth module", "dashboard", "payment gateway", "notifications",
                        "export PDF", "admin panel", "search engine", "API v2"])
        fecha = pick(["15 de mayo", "fin de junio", "agosto", "1 de septiembre"])
        rol = pick(["frontend", "backend", "diseño UX", "QA", "mobile"])
        cat = pick(["A", "B", "C", "D", "E", "F", "G", "H"])
        replacements = {
            "amt": _amount(), "neto": neto, "mes": mes, "client": client[1],
            "n": str(n), "total": str(total), "vel": str(vel),
            "feature": feature, "fecha": fecha, "new_hire": new_hire[1],
            "rol": rol, "pct": _percent(), "cat": cat,
        }
        user_msg = msg_tmpl.format(**replacements)
        facts_list = [
            fact_entry(project[0], ft[0].format(**replacements), ft[1])
            for ft in fact_tmpls
        ]
        output = out("specific", "summary_only", facts=facts_list)
        hint = pick_hint("same", project[1])
        ex = make_example(nodes, hint, project[1],
                          _prev_es(project[1]), user_msg, output)
        examples.append(ex)
    return examples


def gen_g5g_compound():
    """G5g: Compound/multi-part facts (25 examples)."""
    examples = []
    templates = [
        ("Mes {m} de la obra: gastados {g} de {t} presupuestados ({pct}). "
         "Sobrecosto por suba del hierro: {over}.",
         [("Mes {m}: {g} gastados de {t} ({pct})", "user"),
          ("Sobrecosto hierro: {over}", "user")]),
        ("{person} prefiere {opcion1} porque {razon1}. Yo prefiero {opcion2} por {razon2}.",
         [("{person} prefiere {opcion1}: {razon1}", "user"),
          ("Preferencia propia: {opcion2} por {razon2}", "user")]),
        ("Portafolio actual: {pct1} renta fija, {pct2} acciones, {pct3} dólar. "
         "Rendimiento YTD: {rend}.",
         [("Distribución: {pct1} fija, {pct2} acciones, {pct3} dólar", "user"),
          ("Rendimiento YTD: {rend}", "user")]),
        ("Entrenamiento semana {n}: {dist}km total, {sesiones} sesiones. "
         "Promedio por sesión: {prom}km. Mejor tiempo 5K: {t5k}.",
         [("Semana {n}: {dist}km en {sesiones} sesiones, prom {prom}km", "user"),
          ("Mejor 5K: {t5k}", "user")]),
        ("Viaje confirmado: {n1}d {dest1} + {n2}d {dest2}. "
         "Costo total estimado: {costo}. Vuelos ya comprados: {vuelos}.",
         [("Viaje: {n1}d {dest1} + {n2}d {dest2}, total {costo}", "user"),
          ("Vuelos comprados: {vuelos}", "user")]),
    ]
    for _ in range(25):
        tmpl = pick(templates)
        msg_tmpl, fact_tmpls = tmpl
        person = pick(AR_PERSONS)
        dest1 = pick(TRAVEL_DESTINATIONS)
        dest2 = pick([d for d in TRAVEL_DESTINATIONS if d != dest1])
        graph_nodes = [
            existing_node(person[0], person[1], "person", "PERSONAL"),
            existing_node(pick(AR_CITIES)[0], pick(AR_CITIES)[1], "place", "UNIVERSAL"),
        ]
        replacements = {
            "m": str(random.randint(1, 12)), "g": _amount(), "t": _amount(),
            "pct": _percent(), "over": _amount(), "person": person[1],
            "opcion1": pick(["La Herradura", "Palermo", "Güemes", "Fisherton"]),
            "opcion2": pick(["Alberdi", "Villa Crespo", "Centro", "Belgrano"]),
            "razon1": pick(["cercanía al trabajo", "mejor barrio", "más tranquilo"]),
            "razon2": pick(["más espacio", "mejor precio", "más accesible"]),
            "pct1": pick(["30%", "40%", "50%"]),
            "pct2": pick(["25%", "30%", "35%"]),
            "pct3": pick(["20%", "25%", "30%"]),
            "rend": pick(["12%", "18%", "25%", "-5%", "8%"]),
            "n": str(random.randint(1, 52)), "dist": str(random.randint(15, 80)),
            "sesiones": str(random.randint(3, 6)),
            "prom": str(round(random.uniform(3.0, 15.0), 1)),
            "t5k": pick(["24:30", "26:15", "28:00", "22:45", "31:20"]),
            "n1": str(random.randint(3, 10)), "n2": str(random.randint(3, 10)),
            "dest1": dest1[1], "dest2": dest2[1],
            "costo": _amount(), "vuelos": _amount(),
        }
        user_msg = msg_tmpl.format(**replacements)
        facts_list = [
            fact_entry(person[0], ft[0].format(**replacements), ft[1])
            for ft in fact_tmpls
        ]
        output = out("specific", "summary_only", facts=facts_list)
        hint = pick_hint("same")
        ex = make_example(graph_nodes, hint, None, None, user_msg, output)
        examples.append(ex)
    return examples


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 6 — Spanish Personal-Life Entities + Relations (120 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g6a_finanzas():
    """G6a: Financial entities + relations (20 examples)."""
    examples = []
    for _ in range(20):
        nodes, person, city, funds = personal_finance_graph()
        new_fund = pick([f for f in FIN_INSTRUMENTS if f not in funds])
        goal = pick(["vacaciones", "jubilación", "educación", "emergencia", "auto nuevo", "refacción"])
        user_msg = f"Abrí un {new_fund[1]} para {goal}. Arranqué con {_amount()} iniciales."
        new_entity = node(new_fund[0], new_fund[1], new_fund[2], "PERSONAL",
                          facts=[{"text": f"Objetivo: {goal}", "speaker": "user"},
                                 {"text": f"Depósito inicial: {_amount()}", "speaker": "user"}])
        rels = [rel(new_fund[0], person[0], "serves")]
        output = out("specific", "summary_only", entities=[new_entity], relations=rels)
        hint = pick_hint("same", "Finanzas personales")
        ex = make_example(nodes, hint, "Finanzas personales",
                          _prev_es("las finanzas"), user_msg, output)
        examples.append(ex)
    return examples


def gen_g6b_inmobiliario():
    """G6b: Real estate entities + relations (15 examples)."""
    examples = []
    for _ in range(15):
        graph_data = real_estate_graph()
        nodes, person, city, barrio, architect, builder = graph_data
        new_barrio = pick([b for b in AR_BARRIOS if b != barrio])
        lote_id = f"lote_{new_barrio[0]}"
        sup = random.randint(200, 800)
        precio = pick(["25.000 USD", "32.000 USD", "45.000 USD", "55.000 USD", "70.000 USD"])
        user_msg = (f"Fuimos a ver un lote en {new_barrio[1]}, {city[1]}. "
                    f"Son {sup}m2 a {precio}. Tiene todos los servicios.")
        new_entity = node(lote_id, f"Lote {new_barrio[1]}", "place", "PERSONAL",
                          facts=[{"text": f"{sup}m2, precio {precio}", "speaker": "user"}])
        rels = [
            rel(lote_id, new_barrio[0], "located_in"),
            rel(new_barrio[0], city[0], "located_in"),
        ]
        output = out("specific", "summary_only", entities=[new_entity], relations=rels)
        hint = pick_hint("same", f"Búsqueda de terreno")
        ex = make_example(nodes, hint, "Búsqueda de terreno",
                          _prev_es("la búsqueda de terreno"), user_msg, output)
        examples.append(ex)
    return examples


def gen_g6c_salud():
    """G6c: Health entities + relations (15 examples)."""
    examples = []
    for _ in range(15):
        graph_data = health_family_graph()
        nodes, parent, partner, child, city, clinic = graph_data
        doctor_name = pick(AR_PERSONS)
        specialty = pick(MEDICAL)
        clinic_name = pick([b for b in AR_BUSINESSES if "clinica" in b[0].lower() or "farmacia" in b[0].lower()])
        user_msg = (f"El/La {specialty[1].lower()} {doctor_name[1]} de {clinic_name[1]} "
                    f"en {city[1]} nos atendió. Todo bien con {child[1]}.")
        new_entities = [
            node(doctor_name[0], doctor_name[1], "person", "PERSONAL"),
            node(clinic_name[0], clinic_name[1], "organization", "PERSONAL"),
        ]
        rels = [
            rel(doctor_name[0], clinic_name[0], "works_at"),
            rel(clinic_name[0], city[0], "located_in"),
        ]
        output = out("specific", "summary_only", entities=new_entities, relations=rels)
        hint = pick_hint("same", f"Salud de {child[1]}")
        ex = make_example(nodes, hint, f"Salud de {child[1]}",
                          _prev_es(f"la salud de {child[1]}"), user_msg, output)
        examples.append(ex)
    return examples


def gen_g6d_viajes():
    """G6d: Travel entities + relations (15 examples)."""
    examples = []
    for _ in range(15):
        graph_data = travel_graph()
        nodes, person, city_origin, dest, trip_id = graph_data
        barrio = pick(TRAVEL_BARRIOS)
        atraccion = pick(TRAVEL_ATTRACTIONS)
        user_msg = (f"En {dest[1]} nos quedamos en {barrio[1]}. "
                    f"Fuimos al {atraccion[1]}, espectacular.")
        new_entities = [
            node(barrio[0], barrio[1], "place", "UNIVERSAL"),
            node(atraccion[0], atraccion[1], "place", "UNIVERSAL"),
        ]
        rels = [
            rel(barrio[0], dest[0], "located_in"),
            rel(atraccion[0], dest[0], "located_in"),
        ]
        output = out("specific", "summary_only", entities=new_entities, relations=rels)
        hint = pick_hint("same", f"Viaje a {dest[1]}")
        ex = make_example(nodes, hint, f"Viaje a {dest[1]}",
                          _prev_es(f"el viaje a {dest[1]}"), user_msg, output)
        examples.append(ex)
    return examples


def gen_g6e_geografia():
    """G6e: Argentine geography relations (20 examples)."""
    examples = []
    province_map = {
        "mendoza": "Mendoza", "cordoba": "Córdoba", "rosario": "Santa Fe",
        "bahia_blanca": "Buenos Aires", "mar_del_plata": "Buenos Aires",
        "salta": "Salta", "san_martin_andes": "Neuquén",
        "bariloche": "Río Negro", "ushuaia": "Tierra del Fuego",
        "tucuman": "Tucumán", "neuquen": "Neuquén",
        "la_plata": "Buenos Aires", "parana": "Entre Ríos",
    }
    for _ in range(20):
        city = pick(AR_CITIES)
        barrio = pick(AR_BARRIOS)
        prov_name = province_map.get(city[0], "Buenos Aires")
        prov_id = _id(prov_name)
        person = pick(AR_PERSONS)
        nodes = [
            existing_node(person[0], person[1], "person", "PERSONAL"),
            existing_node(city[0], city[1], "place", "UNIVERSAL"),
        ]
        templates = [
            f"Vivimos en {barrio[1]}, {city[1]}. Es un barrio tranquilo, cerca del centro.",
            f"Nos mudamos a {barrio[1]} en {city[1]}. Está a 10 minutos del trabajo.",
            f"El departamento en {barrio[1]}, {city[1]}, tiene 2 ambientes. Zona residencial.",
            f"Conocemos bien {barrio[1]} en {city[1]}. Buen barrio para familias.",
        ]
        user_msg = pick(templates)
        new_entities = [
            node(barrio[0], barrio[1], "place", "UNIVERSAL"),
            node(prov_id, prov_name, "place", "UNIVERSAL"),
        ]
        rels = [
            rel(barrio[0], city[0], "located_in"),
            rel(city[0], prov_id, "located_in"),
        ]
        output = out("specific", "summary_only", entities=new_entities, relations=rels)
        hint = pick_hint("same")
        ex = make_example(nodes, hint, None, None, user_msg, output)
        examples.append(ex)
    return examples


def gen_g6f_persona_org():
    """G6f: Person → Organization relations (20 examples)."""
    examples = []
    for _ in range(20):
        person = pick(AR_PERSONS)
        new_person = pick([p for p in AR_PERSONS if p != person])
        org = pick(AR_BUSINESSES)
        city = pick(AR_CITIES)
        role = pick(["arquitecto", "médica", "electricista", "contadora",
                      "abogada", "ingeniero", "diseñadora", "profesor",
                      "kinesiólogo", "nutricionista", "albañil", "plomero"])
        nodes = [
            existing_node(person[0], person[1], "person", "PERSONAL"),
            existing_node(city[0], city[1], "place", "UNIVERSAL"),
        ]
        templates = [
            f"{new_person[1]} es {role} en {org[1]} de {city[1]}. Lo/La recomendó un amigo.",
            f"Conocimos a {new_person[1]}, {role} de {org[1]}. Tiene {random.randint(5, 25)} años de experiencia.",
            f"El/La {role} {new_person[1]} trabaja en {org[1]}, {city[1]}. Muy profesional.",
        ]
        user_msg = pick(templates)
        new_entities = [
            node(new_person[0], new_person[1], "person", "PERSONAL"),
            node(org[0], org[1], "organization", "PERSONAL"),
        ]
        rels = [
            rel(new_person[0], org[0], "works_at"),
            rel(org[0], city[0], "located_in"),
        ]
        output = out("specific", "summary_only", entities=new_entities, relations=rels)
        hint = pick_hint("same")
        ex = make_example(nodes, hint, None, None, user_msg, output)
        examples.append(ex)
    return examples


def gen_g6g_tech_es():
    """G6g: Tech in Spanish context (15 examples)."""
    examples = []
    for _ in range(15):
        project = pick(PROJECTS_ES)
        techs = pick_n(TECH_ES, random.randint(2, 4))
        person = pick(AR_PERSONS)
        nodes = [
            existing_node(person[0], person[1], "person", "PERSONAL"),
            existing_node(project[0], project[1], "project", "PERSONAL"),
        ]
        tech_names = ", ".join(t[1] for t in techs)
        templates = [
            f"Para {project[1]} estamos usando {tech_names}.",
            f"El stack de {project[1]}: {tech_names}. Todo andando bien.",
            f"Migramos {project[1]} a {tech_names}. Mejor rendimiento.",
        ]
        user_msg = pick(templates)
        new_entities = [
            node(t[0], t[1], "technology", "UNIVERSAL") for t in techs
        ]
        rels = [rel(project[0], t[0], "uses_technology") for t in techs]
        if len(techs) > 1:
            rels.append(rel(techs[0][0], techs[1][0], "depends_on"))
        output = out("specific", "with_chunks", entities=new_entities, relations=rels)
        hint = pick_hint("same", project[1])
        ex = make_example(nodes, hint, project[1],
                          _prev_es(project[1]), user_msg, output)
        examples.append(ex)
    return examples


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 7 — Facts on Existing Entities (100 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g7a_numeric_es():
    """G7a: Numeric facts on existing entities, Spanish (35 examples)."""
    examples = []
    scenarios = [
        ("finance", personal_finance_graph),
        ("real_estate", real_estate_graph),
        ("fitness", fitness_graph),
        ("travel", travel_graph),
        ("work", freelance_graph),
    ]
    fact_templates = {
        "finance": [
            ("El {entity} rindió {pct} este trimestre.", "{entity} rindió {pct} este trimestre"),
            ("Deposité {amt} más en {entity}.", "Depósito adicional: {amt}"),
            ("{entity} ya acumuló {amt}.", "Saldo: {amt}"),
            ("La cuota del {entity} subió a {amt}.", "Cuota actual: {amt}"),
        ],
        "real_estate": [
            ("La obra lleva gastados {amt}.", "Gastados: {amt}"),
            ("El lote se revaluó a {amt}.", "Valor actual: {amt}"),
            ("Avance de obra: {pct} completado.", "Avance: {pct}"),
            ("Próximo pago al constructor: {amt}.", "Próximo pago: {amt}"),
        ],
        "fitness": [
            ("Mi peso hoy: {peso}kg.", "Peso: {peso}kg"),
            ("Corrí {dist}km esta semana.", "Distancia semanal: {dist}km"),
            ("Frecuencia cardíaca en reposo: {fc} bpm.", "FC reposo: {fc} bpm"),
            ("Mejor marca 10K: {tiempo}.", "Marca 10K: {tiempo}"),
        ],
        "travel": [
            ("Ya juntamos {amt} para el viaje.", "Ahorro viaje: {amt}"),
            ("Los vuelos subieron a {amt}.", "Vuelos precio actual: {amt}"),
            ("Hotel reservado: {amt} por noche.", "Hotel: {amt}/noche"),
        ],
        "work": [
            ("El proyecto lleva {n} commits esta semana.", "{n} commits esta semana"),
            ("Facturación del mes: {amt}.", "Facturación mensual: {amt}"),
            ("Avance del sprint: {pct}.", "Sprint: {pct} completado"),
        ],
    }
    for _ in range(35):
        scenario_key, graph_fn = pick(scenarios)
        graph_data = graph_fn()
        nodes = graph_data[0]
        # Pick a random existing entity from the graph
        target_node = pick(nodes)
        target_id = target_node["id"]
        target_label = target_node["label"]
        tmpls = fact_templates[scenario_key]
        tmpl = pick(tmpls)
        msg_tmpl, fact_text_tmpl = tmpl
        replacements = {
            "entity": target_label, "amt": _amount(), "pct": _percent(),
            "peso": str(round(random.uniform(55, 100), 1)),
            "dist": str(random.randint(10, 80)),
            "fc": str(random.randint(50, 75)),
            "tiempo": pick(["42:30", "48:15", "55:00", "1:02:00"]),
            "n": str(random.randint(5, 50)),
        }
        user_msg = msg_tmpl.format(**replacements)
        fact_text = fact_text_tmpl.format(**replacements)
        output = out("specific", "summary_only",
                      facts=[fact_entry(target_id, fact_text, "user")])
        hint = pick_hint("same")
        ex = make_example(nodes, hint, None, None, user_msg, output)
        examples.append(ex)
    return examples


def gen_g7b_status_es():
    """G7b: Status/update facts on existing entities, Spanish (25 examples)."""
    examples = []
    status_templates = [
        "El/La {entity} fue aprobado/a.",
        "{entity} ya está terminado/a.",
        "Cancelamos {entity}.",
        "{entity} se postergó para el mes que viene.",
        "Renovamos {entity} por {n} meses más.",
        "{entity} fue dado/a de baja.",
        "Empezamos con {entity} la semana pasada.",
        "{entity} está en pausa hasta nuevo aviso.",
        "{entity} llegó al objetivo.",
    ]
    for _ in range(25):
        graph_fn = pick([personal_finance_graph, real_estate_graph,
                         health_family_graph, freelance_graph])
        graph_data = graph_fn()
        nodes = graph_data[0]
        target_node = pick(nodes)
        target_id = target_node["id"]
        target_label = target_node["label"]
        tmpl = pick(status_templates)
        n = str(random.randint(3, 24))
        user_msg = tmpl.format(entity=target_label, n=n)
        fact_text = user_msg[:95]  # keep concise
        output = out("specific", "summary_only",
                      facts=[fact_entry(target_id, fact_text, "user")])
        hint = pick_hint("same")
        ex = make_example(nodes, hint, None, None, user_msg, output)
        examples.append(ex)
    return examples


def gen_g7c_en():
    """G7c: Facts on existing entities, English (20 examples)."""
    examples = []
    en_templates = [
        ("The {entity} now handles {n} requests per second.", "{entity}: {n} req/s"),
        ("{entity} was updated to version {ver}.", "Updated to v{ver}"),
        ("We migrated {entity} to a new cluster.", "Migrated to new cluster"),
        ("{entity} uptime is at {pct}.", "Uptime: {pct}"),
        ("The team deployed {entity} to production.", "Deployed to production"),
        ("{entity} now supports {feature}.", "Supports {feature}"),
        ("Bug count for {entity} dropped to {n}.", "Bug count: {n}"),
        ("Performance of {entity} improved by {pct}.", "Performance: +{pct}"),
    ]
    for _ in range(20):
        proj = pick(PROJECTS)
        tech = pick_n(FRONTEND + BACKEND + DATABASES, 2)
        person = pick(PERSONS)
        nodes = [
            existing_node(proj[0], proj[1], "project", "PERSONAL"),
            existing_node(person[0], person[1], "person", "PERSONAL"),
        ] + [existing_node(t[0], t[1], "technology", "UNIVERSAL") for t in tech]
        target = pick(nodes)
        tmpl = pick(en_templates)
        msg_tmpl, fact_text_tmpl = tmpl
        replacements = {
            "entity": target["label"], "n": str(random.randint(100, 50000)),
            "ver": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}",
            "pct": _percent(), "feature": pick(["WebSocket", "GraphQL", "SSO", "dark mode",
                                                 "multi-tenant", "batch exports"]),
        }
        user_msg = msg_tmpl.format(**replacements)
        fact_text = fact_text_tmpl.format(**replacements)
        output = out("specific", "summary_only",
                      facts=[fact_entry(target["id"], fact_text, "user")])
        hint = pick_hint("same", proj[1])
        ex = make_example(nodes, hint, proj[1],
                          f"{proj[1]} is an active project.", user_msg, output)
        examples.append(ex)
    return examples


def gen_g7d_multi():
    """G7d: Multi-fact updates on existing entities (20 examples)."""
    examples = []
    for _ in range(20):
        graph_fn = pick([personal_finance_graph, real_estate_graph, freelance_graph])
        graph_data = graph_fn()
        nodes = graph_data[0]
        if len(nodes) < 2:
            continue
        targets = pick_n(nodes, min(2, len(nodes)))
        spanish = random.random() < 0.5
        if spanish:
            user_msg = (f"{targets[0]['label']} va por {_amount()}. "
                        f"Y {targets[1]['label']} tiene novedades: avance {_percent()}.")
        else:
            user_msg = (f"{targets[0]['label']} is at {_amount()}. "
                        f"Also, {targets[1]['label']} progress is {_percent()}.")
        facts_list = [
            fact_entry(targets[0]["id"], f"Saldo/Estado: {_amount()}" if spanish else f"Status: {_amount()}", "user"),
            fact_entry(targets[1]["id"], f"Avance: {_percent()}" if spanish else f"Progress: {_percent()}", "user"),
        ]
        output = out("specific", "summary_only", facts=facts_list)
        hint = pick_hint("same")
        ex = make_example(nodes, hint, None, None, user_msg, output)
        examples.append(ex)
    return examples


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 8 — Missing Relation Types (30 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g8():
    """G8: Examples for underrepresented relation types (30 examples)."""
    examples = []

    # depends_on (6)
    for _ in range(6):
        proj = pick(PROJECTS_ES)
        t1, t2 = pick_n(TECH_ES, 2)
        spanish = random.random() < 0.6
        if spanish:
            user_msg = f"{proj[1]} depende de {t1[1]} para funcionar. Y {t1[1]} necesita {t2[1]}."
        else:
            user_msg = f"{proj[1]} depends on {t1[1]} to work. And {t1[1]} requires {t2[1]}."
        nodes = [existing_node(proj[0], proj[1], "project", "PERSONAL")]
        ents = [node(t1[0], t1[1], "technology", "UNIVERSAL"),
                node(t2[0], t2[1], "technology", "UNIVERSAL")]
        rels = [rel(proj[0], t1[0], "depends_on"), rel(t1[0], t2[0], "depends_on")]
        output = out("specific", "with_chunks", entities=ents, relations=rels)
        ex = make_example(nodes, pick_hint("same", proj[1]), proj[1], None, user_msg, output)
        examples.append(ex)

    # alternative_to (5)
    for _ in range(5):
        t1, t2 = pick_n(TECH_ES, 2)
        spanish = random.random() < 0.6
        if spanish:
            user_msg = f"Decidimos usar {t1[1]} en vez de {t2[1]}. Es más liviano."
        else:
            user_msg = f"We chose {t1[1]} as an alternative to {t2[1]}. It's lighter."
        proj = pick(PROJECTS_ES)
        nodes = [existing_node(proj[0], proj[1], "project", "PERSONAL")]
        ents = [node(t1[0], t1[1], "technology", "UNIVERSAL"),
                node(t2[0], t2[1], "technology", "UNIVERSAL")]
        rels = [rel(t1[0], t2[0], "alternative_to"), rel(proj[0], t1[0], "uses_technology")]
        output = out("specific", "with_chunks", entities=ents, relations=rels)
        ex = make_example(nodes, pick_hint("same", proj[1]), proj[1], None, user_msg, output)
        examples.append(ex)

    # produces (4)
    for _ in range(4):
        org = pick(AR_BUSINESSES)
        product = pick(["apps mobile", "sistemas web", "reportes mensuales", "análisis de datos"])
        product_id = _id(product)
        spanish = random.random() < 0.6
        if spanish:
            user_msg = f"{org[1]} produce {product} para sus clientes."
        else:
            user_msg = f"{org[1]} produces {product} for their clients."
        nodes = [existing_node(org[0], org[1], "organization", "PERSONAL")]
        ents = [node(product_id, product.title(), "concept", "PERSONAL")]
        rels = [rel(org[0], product_id, "produces")]
        output = out("specific", "summary_only", entities=ents, relations=rels)
        ex = make_example(nodes, pick_hint("same"), None, None, user_msg, output)
        examples.append(ex)

    # resulted_in (4)
    for _ in range(4):
        cause = pick(["suba del hierro", "cambio de proveedor", "update del framework",
                       "migración de base de datos", "reunión con el cliente"])
        cause_id = _id(cause)
        effect = pick(["sobrecosto de obra", "mejora de rendimiento", "delay de 2 semanas",
                        "nuevo requerimiento", "cambio de scope"])
        effect_id = _id(effect)
        user_msg = f"La {cause} resultó en {effect}."
        nodes = []
        ents = [node(cause_id, cause.title(), "event", "PERSONAL"),
                node(effect_id, effect.title(), "event", "PERSONAL")]
        rels = [rel(cause_id, effect_id, "resulted_in")]
        output = out("specific", "summary_only", entities=ents, relations=rels)
        ex = make_example(nodes, pick_hint("same"), None, None, user_msg, output)
        examples.append(ex)

    # created_by (3)
    for _ in range(3):
        person = pick(AR_PERSONS)
        proj = pick(PROJECTS_ES)
        user_msg = f"{proj[1]} fue creado por {person[1]} el año pasado."
        nodes = [existing_node(person[0], person[1], "person", "PERSONAL")]
        ents = [node(proj[0], proj[1], "project", "PERSONAL")]
        rels = [rel(proj[0], person[0], "created_by")]
        output = out("specific", "summary_only", entities=ents, relations=rels)
        ex = make_example(nodes, pick_hint("same"), None, None, user_msg, output)
        examples.append(ex)

    # serves (3)
    for _ in range(3):
        org = pick(AR_BUSINESSES)
        client = pick(AR_PERSONS)
        user_msg = f"{org[1]} nos atiende a nosotros. {client[1]} también es cliente de ahí."
        nodes = [existing_node(client[0], client[1], "person", "PERSONAL")]
        ents = [node(org[0], org[1], "organization", "PERSONAL")]
        rels = [rel(org[0], client[0], "serves")]
        output = out("specific", "summary_only", entities=ents, relations=rels)
        ex = make_example(nodes, pick_hint("same"), None, None, user_msg, output)
        examples.append(ex)

    # member_of (3)
    for _ in range(3):
        person = pick(AR_PERSONS)
        group = pick(["Club de Running Mendoza", "Cooperativa Eléctrica", "Consorcio del edificio",
                       "Equipo de Fútbol Barrial", "Grupo de Inversores"])
        group_id = _id(group)
        user_msg = f"{person[1]} es miembro del {group}."
        nodes = []
        ents = [node(person[0], person[1], "person", "PERSONAL"),
                node(group_id, group, "organization", "PERSONAL")]
        rels = [rel(person[0], group_id, "member_of")]
        output = out("specific", "summary_only", entities=ents, relations=rels)
        ex = make_example(nodes, pick_hint("same"), None, None, user_msg, output)
        examples.append(ex)

    # deployed_on (2)
    for _ in range(2):
        proj = pick(PROJECTS_ES)
        platform = pick([("vercel", "Vercel"), ("railway", "Railway"),
                          ("render", "Render"), ("fly_io", "Fly.io")])
        user_msg = f"{proj[1]} está deployado en {platform[1]}."
        nodes = [existing_node(proj[0], proj[1], "project", "PERSONAL")]
        ents = [node(platform[0], platform[1], "technology", "UNIVERSAL")]
        rels = [rel(proj[0], platform[0], "deployed_on")]
        output = out("specific", "summary_only", entities=ents, relations=rels)
        ex = make_example(nodes, pick_hint("same", proj[1]), proj[1], None, user_msg, output)
        examples.append(ex)

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 9 — Intent Calibration for Personal Domains (30 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g9():
    """G9: Intent calibration for personal domains (30 examples)."""
    examples = []
    # overview (6)
    overview_msgs = [
        "Cómo venimos con la obra de la casa?",
        "Haceme un resumen de mis finanzas.",
        "Cómo está mi portafolio de inversiones?",
        "Qué avances hubo esta semana en el proyecto?",
        "Dame un panorama general de la salud de la familia.",
        "Cómo viene el plan de entrenamiento?",
    ]
    for msg in overview_msgs:
        nodes = [existing_node(pick(AR_PERSONS)[0], pick(AR_PERSONS)[1], "person", "PERSONAL")]
        output = out("overview", "summary_only")
        ex = make_example(nodes, pick_hint("same"), None, None, msg, output)
        examples.append(ex)

    # specific (8)
    specific_cases = [
        ("Cuánto nos costó el hierro para la estructura?", True),
        ("Cuál es mi plan de entrenamiento de esta semana?", True),
        ("Cuánto rindió el fondo conservador este trimestre?", True),
        ("Qué vacunas le faltan a Emilia?", True),
        ("Cuánto sale el vuelo a Madrid?", True),
        ("Quién es el pediatra que nos atendió?", True),
        ("Cuánto facturé en marzo?", True),
        ("Qué tecnologías usa el proyecto?", True),
    ]
    for msg, has_content in specific_cases:
        nodes = [existing_node(pick(AR_PERSONS)[0], pick(AR_PERSONS)[1], "person", "PERSONAL")]
        output = out("specific", "with_chunks" if has_content else "summary_only")
        ex = make_example(nodes, pick_hint("same"), None, None, msg, output)
        examples.append(ex)

    # followup (8)
    followup_msgs = [
        "Contame más sobre eso.",
        "Y qué pasó con el permiso de construcción?",
        "Seguí con lo del crédito hipotecario.",
        "Y el entrenador qué dijo?",
        "Dale, ampliate sobre los CEDEARs.",
        "Más detalles del presupuesto.",
        "Y el tema de las vacunas?",
        "Profundizá en el sprint actual.",
    ]
    for msg in followup_msgs:
        nodes = [existing_node(pick(AR_PERSONS)[0], pick(AR_PERSONS)[1], "person", "PERSONAL")]
        output = out("followup", "with_chunks")
        ex = make_example(nodes, pick_hint("same"), None, "Te conté sobre los avances.", msg, output)
        examples.append(ex)

    # chat (8)
    chat_msgs = [
        "Genial, qué buena noticia!",
        "Uf, qué estrés con la obra.",
        "Buenísimo, me alegra.",
        "Dale, gracias por la info.",
        "Sí, estoy de acuerdo.",
        "Ja, qué locura.",
        "Perfecto, después vemos.",
        "Gracias, está muy claro.",
    ]
    for msg in chat_msgs:
        nodes = [existing_node(pick(AR_PERSONS)[0], pick(AR_PERSONS)[1], "person", "PERSONAL")]
        output = out("chat", "summary_only")
        ex = make_example(nodes, pick_hint("same"), None, None, msg, output)
        examples.append(ex)

    return examples


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 10 — Edge Cases + Robustness (60 examples)
# ═══════════════════════════════════════════════════════════════════════════

def gen_g10a_empty():
    """G10a: Empty extraction in personal domains (15 examples)."""
    examples = []
    msgs = [
        "Qué hora es?", "Estaba pensando en voz alta.",
        "No sé, vos qué opinás?", "Puede ser, no estoy seguro.",
        "Dejame pensar un momento.", "Ah, mirá vos.",
        "Bueno, después vemos eso.", "No me acuerdo ahora.",
        "Me parece que sí.", "Pasá el mate.",
        "Qué loco, no?", "No tengo idea.",
        "Dale, charlamos mañana.", "Sí sí, todo bien.",
        "Ni idea, habría que averiguar.",
    ]
    for msg in msgs:
        nodes = [existing_node(pick(AR_PERSONS)[0], pick(AR_PERSONS)[1], "person", "PERSONAL")]
        output = out("chat", "summary_only")
        ex = make_example(nodes, pick_hint("same"), None, None, msg, output)
        examples.append(ex)
    return examples


def gen_g10b_topic_change():
    """G10b: Topic changes in Spanish (10 examples)."""
    examples = []
    changes = [
        ("Dejemos las finanzas. Hablemos del viaje a Europa.", "Viaje a Europa"),
        ("Cambiando de tema: cómo viene la obra?", "Proyecto casa"),
        ("Bueno, pasemos a otro tema. Qué onda el entrenamiento?", "Entrenamiento"),
        ("Basta de obra. Contame de las inversiones.", "Inversiones"),
        ("Che, hablemos de otra cosa. Cómo está Emilia?", "Salud familia"),
        ("Dejá eso. Necesito ver el tema del trabajo.", "Trabajo"),
        ("Pasemos a lo del viaje. Ya compraron los vuelos?", "Viaje"),
        ("Suficiente de finanzas por hoy. Hablemos del gym.", "Fitness"),
        ("Cambiemos: qué novedades hay del proyecto de código?", "Proyecto código"),
        ("OK, ahora hablemos de la mudanza.", "Mudanza"),
    ]
    for msg, new_topic in changes:
        nodes = [existing_node(pick(AR_PERSONS)[0], pick(AR_PERSONS)[1], "person", "PERSONAL")]
        output = out("overview", "summary_only", action="changed", label=new_topic)
        ex = make_example(nodes, pick_hint("changed"), None, None, msg, output)
        examples.append(ex)
    return examples


def gen_g10c_first_msg():
    """G10c: Rich first messages in Spanish (10 examples)."""
    examples = []
    first_msgs = [
        {
            "msg": "Quiero empezar a organizar mis finanzas. Gano 4.500.000 ARS por mes, soy monotributista categoría D.",
            "entities": [node(_id("finanzas_personales"), "Finanzas Personales", "concept", "PERSONAL",
                              facts=[{"text": "Ingreso: 4.500.000 ARS/mes, monotributo cat D", "speaker": "user"}])],
            "topic": "Finanzas personales",
        },
        {
            "msg": "Estamos buscando terreno para construir en Mendoza. Presupuesto: hasta 40.000 USD.",
            "entities": [
                node("busqueda_terreno", "Búsqueda de Terreno", "project", "PERSONAL",
                     facts=[{"text": "Presupuesto hasta 40.000 USD", "speaker": "user"}]),
                node("mendoza", "Mendoza", "place", "UNIVERSAL"),
            ],
            "relations": [rel("busqueda_terreno", "mendoza", "located_in")],
            "topic": "Búsqueda de terreno",
        },
        {
            "msg": "Arranco un proyecto nuevo: una app para dividir gastos entre amigos. Se va a llamar GastosYa.",
            "entities": [node("gastosya", "GastosYa", "project", "PERSONAL")],
            "topic": "GastosYa",
        },
        {
            "msg": "Necesito planificar un viaje a Roma para marzo. Somos 2 adultos, presupuesto de 5.000 USD.",
            "entities": [
                node("viaje_roma", "Viaje a Roma", "event", "PERSONAL",
                     facts=[{"text": "Marzo, 2 adultos, presupuesto 5.000 USD", "speaker": "user"}]),
                node("roma", "Roma", "place", "UNIVERSAL"),
            ],
            "topic": "Viaje a Roma",
        },
        {
            "msg": "Quiero empezar a correr. Nunca hice ejercicio formal. Mi objetivo es una 5K.",
            "entities": [node("running", "Running", "concept", "PERSONAL",
                              facts=[{"text": "Principiante, objetivo 5K", "speaker": "user"}])],
            "topic": "Running",
        },
        {
            "msg": "Mi hijo Bautista cumple 1 año la semana que viene. Estamos viendo el tema de las vacunas.",
            "entities": [node("bautista", "Bautista", "person", "PERSONAL",
                              facts=[{"text": "Cumple 1 año", "speaker": "user"}])],
            "topic": "Salud de Bautista",
        },
        {
            "msg": "Empecé a freelancear como diseñadora UX. Mi primer cliente es una fintech de Córdoba.",
            "entities": [
                node("freelance_ux", "Freelance UX", "project", "PERSONAL"),
                node("fintech_cordoba", "Fintech Córdoba", "organization", "PERSONAL"),
                node("cordoba", "Córdoba", "place", "UNIVERSAL"),
            ],
            "relations": [rel("fintech_cordoba", "cordoba", "located_in")],
            "topic": "Freelance UX",
        },
        {
            "msg": "Estamos refaccionando la cocina. El plomero viene mañana. Presupuesto total: 2.000.000 ARS.",
            "entities": [node("refaccion_cocina", "Refacción Cocina", "project", "PERSONAL",
                              facts=[{"text": "Presupuesto: 2.000.000 ARS", "speaker": "user"}])],
            "topic": "Refacción cocina",
        },
        {
            "msg": "Me diagnosticaron tendinitis en la rodilla. El traumatólogo me recetó kinesiología.",
            "entities": [node("tendinitis_rodilla", "Tendinitis rodilla", "concept", "PERSONAL",
                              facts=[{"text": "Tratamiento: kinesiología", "speaker": "user"}])],
            "topic": "Salud",
        },
        {
            "msg": "Abrí una cuenta en Balanz para empezar a invertir. Depósito inicial: 500.000 ARS.",
            "entities": [node("cuenta_balanz", "Cuenta Balanz", "concept", "PERSONAL",
                              facts=[{"text": "Depósito inicial: 500.000 ARS", "speaker": "user"}]),
                         node("balanz", "Balanz", "organization", "UNIVERSAL")],
            "topic": "Inversiones",
        },
    ]
    for case in first_msgs:
        output = out("overview", "summary_only", action="changed", label=case["topic"],
                      entities=case["entities"],
                      relations=case.get("relations", []),
                      facts=case.get("facts", []))
        ex = make_example([], pick_hint("first"), "null", None, case["msg"], output)
        examples.append(ex)
    return examples


def gen_g10d_entity_only():
    """G10d: Entity-only extraction, no facts (10 examples)."""
    examples = []
    for _ in range(10):
        person = pick(AR_PERSONS)
        new_person = pick([p for p in AR_PERSONS if p != person])
        city = pick(AR_CITIES)
        nodes = [existing_node(person[0], person[1], "person", "PERSONAL")]
        templates = [
            f"Conocimos a {new_person[1]} en {city[1]}.",
            f"{new_person[1]} vive en {city[1]}.",
            f"Nos recomendaron a {new_person[1]} de {city[1]}.",
        ]
        user_msg = pick(templates)
        ents = [node(new_person[0], new_person[1], "person", "PERSONAL")]
        rels = [rel(new_person[0], city[0], "located_in")]
        output = out("specific", "summary_only", entities=ents, relations=rels)
        ex = make_example(nodes, pick_hint("same"), None, None, user_msg, output)
        examples.append(ex)
    return examples


def gen_g10e_informal():
    """G10e: Informal Argentine register (8 examples)."""
    examples = []
    informal_msgs = [
        ("Re piola el barrio, tiene de todo cerca.", "chat", "summary_only"),
        ("Está volando el dólar, no? Habría que comprar ya.", "specific", "summary_only"),
        ("Maaaal, la obra no termina más jajaja.", "chat", "summary_only"),
        ("Posta? No sabía que costaba tanto.", "chat", "summary_only"),
        ("Tremendo laburo le están metiendo al proyecto.", "chat", "summary_only"),
        ("Ojo que el plazo fijo vence la semana que viene eh.", "specific", "summary_only"),
        ("Nah, olvidate, eso sale carísimo.", "chat", "summary_only"),
        ("Genio el arquitecto, solucionó todo en 5 minutos.", "chat", "summary_only"),
    ]
    for msg, intent, retrieval in informal_msgs:
        nodes = [existing_node(pick(AR_PERSONS)[0], pick(AR_PERSONS)[1], "person", "PERSONAL")]
        output = out(intent, retrieval)
        ex = make_example(nodes, pick_hint("same"), None, None, msg, output)
        examples.append(ex)
    return examples


def gen_g10f_numeric():
    """G10f: Long numeric messages with multiple facts (7 examples)."""
    examples = []
    numeric_msgs = [
        {
            "msg": "Resumen del mes: alquiler 450.000 ARS, supermercado 380.000 ARS, servicios 95.000 ARS, nafta 120.000 ARS, obra social 85.000 ARS. Total: 1.130.000 ARS.",
            "facts": [fact_entry(pick(AR_PERSONS)[0], "Gastos mensuales: 1.130.000 ARS total", "user")],
        },
        {
            "msg": "Portafolio: 40% FCI money market (2.5M ARS), 25% CEDEARs (1.6M ARS), 20% plazo fijo (1.3M ARS), 15% dólar MEP (500 USD).",
            "facts": [fact_entry(pick(FIN_INSTRUMENTS)[0], "Portafolio: 40% FCI, 25% CEDEARs, 20% PF, 15% MEP", "user")],
        },
        {
            "msg": "Presupuesto obra actualizado: terreno 32K USD, estructura 45K USD, mampostería 25K USD, instalaciones 20K USD, terminaciones 35K USD, imprevistos 15K USD. Total: 172K USD.",
            "facts": [
                fact_entry(pick(AR_BARRIOS)[0], "Presupuesto obra: 172K USD total", "user"),
                fact_entry(pick(AR_BARRIOS)[0], "Desglose: terreno 32K, estructura 45K, mampostería 25K, inst 20K, term 35K, imprevistos 15K", "user"),
            ],
        },
        {
            "msg": "Nutrición semanal: 2500 kcal/día entrenamiento, 2000 kcal/día descanso. Proteína: 120g/día. Hidratación: 3L agua/día.",
            "facts": [fact_entry(pick(AR_PERSONS)[0], "Nutrición: 2500kcal entreno, 2000kcal descanso, 120g proteína, 3L agua", "user")],
        },
        {
            "msg": "Itinerario final: Madrid 5 noches (hotel 120 EUR/noche), Barcelona 4 noches (Airbnb 90 EUR/noche), vuelo interno 85 EUR. Total alojamiento: 960 EUR.",
            "facts": [
                fact_entry(pick(TRAVEL_DESTINATIONS)[0], "Madrid 5n x 120EUR + Barcelona 4n x 90EUR = 960EUR alojamiento", "user"),
            ],
        },
        {
            "msg": "Sprint 15: completados 18/22 tickets. Velocidad: 45 puntos. Bugs: 3 críticos resueltos, 2 pendientes. Cobertura de tests: 78%.",
            "facts": [
                fact_entry(pick(PROJECTS_ES)[0], "Sprint 15: 18/22 tickets, 45pts velocidad", "user"),
                fact_entry(pick(PROJECTS_ES)[0], "Bugs: 3 críticos resueltos, 2 pendientes. Tests: 78%", "user"),
            ],
        },
        {
            "msg": "Control pediátrico 12 meses: peso 10.2kg (percentil 50), talla 76cm (percentil 60), perímetro cefálico 46cm. Vacunas al día.",
            "facts": [fact_entry(pick(["emilia", "bautista", "olivia", "lautaro"]),
                                 "12m: 10.2kg (P50), 76cm (P60), PC 46cm. Vacunas OK", "user")],
        },
    ]
    for case in numeric_msgs:
        person = pick(AR_PERSONS)
        nodes = [existing_node(person[0], person[1], "person", "PERSONAL")]
        output = out("specific", "summary_only", facts=case["facts"])
        ex = make_example(nodes, pick_hint("same"), None, None, case["msg"], output)
        examples.append(ex)
    return examples


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    random.seed(args.seed)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    groups = {
        "g5_facts_personal": (
            gen_g5a_casa() + gen_g5b_finanzas() + gen_g5c_salud() +
            gen_g5d_viajes() + gen_g5e_fitness() + gen_g5f_trabajo() +
            gen_g5g_compound()
        ),
        "g6_entities_relations": (
            gen_g6a_finanzas() + gen_g6b_inmobiliario() + gen_g6c_salud() +
            gen_g6d_viajes() + gen_g6e_geografia() + gen_g6f_persona_org() +
            gen_g6g_tech_es()
        ),
        "g7_facts_existing": (
            gen_g7a_numeric_es() + gen_g7b_status_es() +
            gen_g7c_en() + gen_g7d_multi()
        ),
        "g8_missing_relations": gen_g8(),
        "g9_intent_personal": gen_g9(),
        "g10_edge_cases": (
            gen_g10a_empty() + gen_g10b_topic_change() + gen_g10c_first_msg() +
            gen_g10d_entity_only() + gen_g10e_informal() + gen_g10f_numeric()
        ),
    }

    total = 0
    for group_name, examples in groups.items():
        path = OUTPUT_DIR / f"v3_new_{group_name}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        # Validate
        stats = validate_s1_jsonl(str(path))
        valid_pct = stats["schema_valid_rate"] * 100
        print(f"  {group_name}: {len(examples)} examples, schema valid: {valid_pct:.0f}%")
        if stats["errors"]:
            for line_num, err in stats["errors"][:3]:
                print(f"    ERROR line {line_num}: {err[:100]}")
        total += len(examples)

    print(f"\nTotal new examples: {total}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

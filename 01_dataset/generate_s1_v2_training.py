#!/usr/bin/env python3
"""
Generate v2 training data for Acervo S1 model.

Produces ~390 NEW examples covering:
  A. Intent classification (100)
  B. Retrieval decision (80)
  C. Code extraction (50)
  D. Literature/prose extraction (40)
  E. Documentation extraction (40)
  F. S1.5 improvement — assistant response extraction (30)
  G. S1 failure variations from v0.4 benchmarks (50)

Usage:
    python 01_dataset/generate_s1_v2_training.py [--seed 42]
"""

import json
import random
import argparse
from pathlib import Path
from copy import deepcopy

# Import shared helpers and pools from v1 generator
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
from schema import S1_SYSTEM_PROMPT, validate_s1

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "training_data" / "v2"

# ═══════════════════════════════════════════════════════════════════════════
# Additional pools for v2
# ═══════════════════════════════════════════════════════════════════════════

CODE_SNIPPETS = [
    {
        "language": "TypeScript",
        "description": "Auth middleware",
        "code": """export async function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.split('Bearer ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });
  const payload = await verifyJWT(token);
  req.user = payload;
  next();
}""",
        "entities": [
            ("auth_middleware", "Auth Middleware", "concept", "PERSONAL"),
            ("jwt", "JWT", "technology", "UNIVERSAL"),
        ],
        "relations": [("auth_middleware", "jwt", "uses_technology")],
    },
    {
        "language": "Python",
        "description": "FastAPI endpoint",
        "code": """@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == user.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user = User(**user.model_dump())
    db.add(new_user)
    await db.commit()
    return new_user""",
        "entities": [
            ("user_endpoint", "User Creation Endpoint", "concept", "PERSONAL"),
            ("fastapi", "FastAPI", "technology", "UNIVERSAL"),
            ("sqlalchemy", "SQLAlchemy", "technology", "UNIVERSAL"),
        ],
        "relations": [("user_endpoint", "fastapi", "uses_technology")],
    },
    {
        "language": "TypeScript",
        "description": "React component",
        "code": """export function Dashboard({ userId }: { userId: string }) {
  const { data, isLoading } = useQuery(['dashboard', userId], () => fetchDashboard(userId));
  if (isLoading) return <Skeleton />;
  return (
    <div className="grid grid-cols-3 gap-4">
      <MetricsCard data={data.metrics} />
      <ChartPanel data={data.charts} />
      <ActivityFeed items={data.activity} />
    </div>
  );
}""",
        "entities": [
            ("dashboard_component", "Dashboard Component", "concept", "PERSONAL"),
            ("react_query", "React Query", "technology", "UNIVERSAL"),
            ("react", "React", "technology", "UNIVERSAL"),
        ],
        "relations": [("dashboard_component", "react", "uses_technology"),
                      ("dashboard_component", "react_query", "uses_technology")],
    },
    {
        "language": "Python",
        "description": "Database migration",
        "code": """def upgrade():
    op.create_table(
        'invoices',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('client_id', sa.UUID(), sa.ForeignKey('clients.id')),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', sa.Enum('draft', 'sent', 'paid', 'overdue')),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_invoices_client', 'invoices', ['client_id'])""",
        "entities": [
            ("invoices_table", "Invoices Table", "concept", "PERSONAL"),
            ("alembic", "Alembic", "technology", "UNIVERSAL"),
        ],
        "relations": [],
    },
    {
        "language": "YAML",
        "description": "Docker Compose config",
        "code": """services:
  api:
    build: ./api
    ports: ["8000:8000"]
    depends_on: [db, redis]
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/app
  db:
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]""",
        "entities": [
            ("docker_compose", "Docker Compose", "technology", "UNIVERSAL"),
            ("postgresql", "PostgreSQL", "technology", "UNIVERSAL"),
            ("redis", "Redis", "technology", "UNIVERSAL"),
        ],
        "relations": [],
    },
    {
        "language": "TypeScript",
        "description": "Supabase RLS policy",
        "code": """-- Row Level Security for user data
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = user_id);""",
        "entities": [
            ("rls_policies", "RLS Policies", "concept", "PERSONAL"),
            ("supabase", "Supabase", "technology", "UNIVERSAL"),
        ],
        "relations": [],
    },
]

# Code snippets that should produce NO entities (utility/boilerplate)
EMPTY_CODE_SNIPPETS = [
    {
        "language": "CSS",
        "code": """.container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
.flex { display: flex; }
.grid { display: grid; }
.hidden { display: none; }""",
    },
    {
        "language": "TypeScript",
        "code": """export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}""",
    },
    {
        "language": "Python",
        "code": """import logging
logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO"):
    logging.basicConfig(level=getattr(logging, level), format="%(asctime)s %(name)s %(levelname)s %(message)s")""",
    },
]

PROSE_PASSAGES = [
    {
        "text": "The detective examined the room carefully. Watson stood by the door, watching Holmes pace between the windows. 'There are three distinct sets of footprints,' Holmes declared, pointing at the carpet near the desk. Mrs. Hudson had found the body that morning.",
        "entities": [
            ("sherlock_holmes", "Sherlock Holmes", "person", "UNIVERSAL"),
            ("dr_watson", "Dr. Watson", "person", "UNIVERSAL"),
            ("mrs_hudson", "Mrs. Hudson", "person", "UNIVERSAL"),
        ],
        "relations": [],
        "facts": [("sherlock_holmes", "Found three distinct sets of footprints at the scene", "user")],
    },
    {
        "text": "The Battle of Helm's Deep lasted through the night. Aragorn led the defense alongside Legolas and Gimli, while Gandalf rode to find Eomer and the Riders of Rohan. At dawn, Gandalf returned with reinforcements, turning the tide of battle against Saruman's army of Uruk-hai.",
        "entities": [
            ("helms_deep", "Helm's Deep", "place", "UNIVERSAL"),
            ("eomer", "Eomer", "person", "UNIVERSAL"),
            ("uruk_hai_army", "Uruk-hai Army", "concept", "UNIVERSAL"),
        ],
        "relations": [
            ("eomer", "helms_deep", "participated_in"),
        ],
        "facts": [
            ("aragorn", "Led the defense at Helm's Deep alongside Legolas and Gimli", "user"),
            ("gandalf", "Rode to find Eomer and returned at dawn with reinforcements", "user"),
        ],
    },
    {
        "text": "Elizabeth Bennet refused Mr. Darcy's first proposal at Hunsford. She accused him of separating Jane and Bingley, and of mistreating Wickham. Darcy was shocked by the refusal and wrote her a letter the next day explaining his actions and revealing Wickham's true character.",
        "entities": [
            ("elizabeth_bennet", "Elizabeth Bennet", "person", "UNIVERSAL"),
            ("mr_darcy", "Mr. Darcy", "person", "UNIVERSAL"),
            ("wickham", "Wickham", "person", "UNIVERSAL"),
            ("jane_bennet", "Jane Bennet", "person", "UNIVERSAL"),
            ("bingley", "Mr. Bingley", "person", "UNIVERSAL"),
            ("hunsford", "Hunsford", "place", "UNIVERSAL"),
        ],
        "relations": [],
        "facts": [
            ("elizabeth_bennet", "Refused Darcy's first proposal at Hunsford", "user"),
            ("mr_darcy", "Wrote a letter explaining his actions after being refused", "user"),
        ],
    },
    {
        "text": "El coronel Aureliano Buendía organizó treinta y dos levantamientos armados y los perdió todos. De sus diecisiete hijos varones con diecisiete mujeres distintas, todos fueron exterminados uno tras otro en una sola noche. Sobrevivió a un fusilamiento, a la guerra y a la soledad.",
        "entities": [
            ("aureliano_buendia", "Coronel Aureliano Buendía", "person", "UNIVERSAL"),
        ],
        "relations": [],
        "facts": [
            ("aureliano_buendia", "Organized 32 armed uprisings and lost them all", "user"),
            ("aureliano_buendia", "Had 17 sons with 17 different women, all killed in one night", "user"),
        ],
    },
]

DOC_PASSAGES = [
    {
        "text": "# Beacon v2.0 Release Notes\n\nNew features:\n- WebSocket support for real-time dashboards\n- Multi-tenant data isolation\n- Export to PDF and CSV\n\nBreaking changes:\n- Minimum Node.js version bumped to 18\n- REST polling deprecated, use WebSocket instead\n\nContributors: Alice Chen, Bob Martinez",
        "entities": [
            ("websocket_support", "WebSocket Support", "concept", "PERSONAL"),
            ("multi_tenant", "Multi-tenant Isolation", "concept", "PERSONAL"),
        ],
        "relations": [
            ("websocket_support", "beacon", "part_of"),
            ("multi_tenant", "beacon", "part_of"),
        ],
        "facts": [
            ("beacon", "v2.0 requires minimum Node.js 18", "user"),
            ("beacon", "REST polling deprecated in v2.0, replaced by WebSocket", "user"),
            ("alice_chen", "Contributed to Beacon v2.0 release", "user"),
            ("bob_martinez", "Contributed to Beacon v2.0 release", "user"),
        ],
    },
    {
        "text": "## Architecture Decision Record: Database Selection\n\nDate: 2025-03-15\nStatus: Accepted\nDeciders: Alice Chen, Bob Martinez\n\nContext: We need a database for the Beacon project that supports real-time subscriptions.\n\nDecision: Use Supabase (PostgreSQL) instead of MongoDB.\n\nRationale:\n- Native real-time via Postgres changes\n- Row Level Security for multi-tenancy\n- Better SQL ecosystem for analytics",
        "entities": [
            ("db_adr", "Database Selection ADR", "document", "PERSONAL"),
        ],
        "relations": [
            ("db_adr", "beacon", "documented_in"),
        ],
        "facts": [
            ("beacon", "Chose Supabase over MongoDB for real-time subscriptions and RLS", "user"),
        ],
    },
    {
        "text": "Sprint 14 Review — 2025-04-01\n\nCompleted:\n- AUTH-142: Implement OAuth2 with Google (Alice)\n- DASH-89: Real-time chart updates (Bob)\n- API-201: Rate limiting middleware (Priya)\n\nCarried over:\n- DASH-95: PDF export (blocked by design review)\n\nVelocity: 21 points (target: 20)",
        "entities": [
            ("sprint_14", "Sprint 14", "event", "PERSONAL"),
            ("oauth2_google", "OAuth2 with Google", "concept", "PERSONAL"),
            ("rate_limiting", "Rate Limiting Middleware", "concept", "PERSONAL"),
        ],
        "relations": [],
        "facts": [
            ("alice_chen", "Implemented OAuth2 with Google (AUTH-142)", "user"),
            ("bob_martinez", "Implemented real-time chart updates (DASH-89)", "user"),
            ("priya_sharma", "Implemented rate limiting middleware (API-201)", "user"),
        ],
    },
    {
        "text": "## API Reference: POST /api/v1/users\n\nCreates a new user account.\n\nRequest body:\n```json\n{\"name\": \"string\", \"email\": \"string\", \"role\": \"admin|user|viewer\"}\n```\n\nResponse: 201 Created\n```json\n{\"id\": \"uuid\", \"name\": \"string\", \"email\": \"string\", \"created_at\": \"datetime\"}\n```\n\nErrors: 409 Conflict (email exists), 422 Validation Error",
        "entities": [
            ("users_api", "Users API Endpoint", "concept", "PERSONAL"),
        ],
        "relations": [("users_api", "beacon", "part_of")],
        "facts": [
            ("users_api", "POST /api/v1/users creates user accounts with name, email, role", "user"),
            ("users_api", "Supports three roles: admin, user, viewer", "user"),
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def make_v2_example(existing_nodes, topic_hint, current_topic, prev_assistant, user_msg, output):
    """Build a complete v2 training example with intent + retrieval."""
    return {
        "messages": [
            {"role": "system", "content": S1_SYSTEM_PROMPT},
            {"role": "user", "content": format_user_input(
                existing_nodes, topic_hint, current_topic, prev_assistant, user_msg
            )},
            {"role": "assistant", "content": json.dumps(output, ensure_ascii=False)},
        ]
    }


def v2_output(intent, retrieval, action="same", label=None, entities=None, relations=None, facts=None):
    """Build a v2 output dict."""
    topic = {"action": action}
    if label and action != "same":
        topic["label"] = label
    else:
        topic["label"] = label
    return {
        "intent": intent,
        "topic": topic,
        "retrieval": retrieval,
        "entities": entities or [],
        "relations": relations or [],
        "facts": facts or [],
    }


# ═══════════════════════════════════════════════════════════════════════════
# A. Intent Classification Examples (~100)
# ═══════════════════════════════════════════════════════════════════════════

def gen_intent_overview():
    """Generate overview intent examples."""
    examples = []

    # With software graph context
    for _ in range(8):
        g = software_graph("medium")
        nodes, proj = g[0], g[1]

        messages_en = [
            f"What is {proj[1]} about?",
            f"Give me an overview of {proj[1]}.",
            f"Describe the {proj[1]} project.",
            f"What technologies does {proj[1]} use?",
            f"How many people work on {proj[1]}?",
            f"What's the overall status of the project?",
            f"List the main components of {proj[1]}.",
            f"Tell me about {proj[1]}.",
        ]
        messages_es = [
            f"¿De qué se trata {proj[1]}?",
            f"Dame un resumen de {proj[1]}.",
            f"Describime el proyecto {proj[1]}.",
            f"¿Qué tecnologías usa {proj[1]}?",
            f"¿Cuánta gente trabaja en {proj[1]}?",
            f"¿Cuál es el estado general del proyecto?",
        ]

        msg = pick(messages_es) if spanish_chance() else pick(messages_en)
        output = v2_output("overview", "summary_only")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development", None, msg, output
        ))

    # Without context (first message)
    for _ in range(5):
        messages = [
            "What is this project?",
            "What is this application about?",
            "Tell me about this codebase.",
            "What does this project do?",
            "¿De qué se trata este proyecto?",
            "¿Qué es esta aplicación?",
            "Describime este proyecto.",
            "What are we looking at here?",
        ]
        output = v2_output("overview", "summary_only")
        examples.append(make_v2_example([], "unresolved — classify the topic yourself", None, None, pick(messages), output))

    # With literature context
    for _ in range(5):
        g = literature_graph(size="small")
        nodes, chars, places, title = g[0], g[1], g[2], g[3]
        messages = [
            f"What is {title} about?",
            f"Give me a summary of {title}.",
            f"¿De qué trata {title}?",
            f"What's the general plot?",
            f"Who are the main characters?",
        ]
        output = v2_output("overview", "summary_only")
        examples.append(make_v2_example(nodes, pick_hint("same"), title, None, pick(messages), output))

    # With business context
    for _ in range(5):
        g = business_graph("small")
        nodes = g[0]
        org = g[1]
        messages = [
            f"Tell me about {org[1]}.",
            f"What does {org[1]} do?",
            f"How is the team structured at {org[1]}?",
            f"¿Cómo está organizado el equipo en {org[1]}?",
            f"What's the company overview?",
        ]
        output = v2_output("overview", "summary_only")
        examples.append(make_v2_example(nodes, pick_hint("same"), f"{org[1]} team", None, pick(messages), output))

    # General overview questions (no specific entities)
    general_overview = [
        "How many files are indexed?",
        "What's the overall structure?",
        "¿Cuántos documentos hay?",
        "List all the topics we've discussed.",
        "Give me a summary of everything.",
        "Dame un resumen general.",
        "What have we covered so far?",
    ]
    for msg in general_overview:
        g = software_graph("small")
        output = v2_output("overview", "summary_only")
        examples.append(make_v2_example(g[0], pick_hint("same"), "General", None, msg, output))

    return examples[:25]


def gen_intent_specific():
    """Generate specific intent examples."""
    examples = []

    # Specific questions about code/tech
    for _ in range(8):
        g = software_graph("medium")
        nodes, proj, org, fe, be, db = g[0], g[1], g[2], g[3], g[4], g[5]
        people = g[6]

        messages_en = [
            f"How does auth work in {proj[1]}?",
            f"Show me the {be[1]} controller for users.",
            f"What's the database schema for {proj[1]}?",
            f"How is {fe[1]} configured in {proj[1]}?",
            f"What's {people[0][1]}'s role exactly?",
            f"What endpoints does the API expose?",
            f"How does the deployment pipeline work?",
            f"What's the error handling strategy?",
        ]
        messages_es = [
            f"¿Cómo funciona la autenticación en {proj[1]}?",
            f"¿Cuál es el esquema de la base de datos?",
            f"¿Qué rol tiene {people[0][1]} exactamente?",
            f"¿Cómo está configurado {fe[1]}?",
        ]

        msg = pick(messages_es) if spanish_chance() else pick(messages_en)
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            f"I can help you with {proj[1]}.", msg, output
        ))

    # Specific questions about literature
    for _ in range(5):
        g = literature_graph(size="medium")
        nodes, chars, places, title = g[0], g[1], g[2], g[3]
        char = pick(chars)
        messages = [
            f"What happens to {char[1]} in chapter 2?",
            f"Who is {char[1]}?",
            f"What's the relationship between {chars[0][1]} and {chars[1][1]}?",
            f"What happened at {places[0][1]}?",
            f"¿Qué le pasa a {char[1]}?",
        ]
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(nodes, pick_hint("same"), title, None, pick(messages), output))

    # Specific questions about people
    for _ in range(5):
        g = business_graph("medium")
        nodes = g[0]
        people = g[2]
        person = pick(people)
        messages = [
            f"What's {person[1]}'s email?",
            f"When did {person[1]} join the team?",
            f"What projects is {person[1]} working on?",
            f"¿Cuándo empezó {person[1]}?",
            f"What's {person[1]}'s phone number?",
        ]
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{g[1][1]} team", None, pick(messages), output
        ))

    # Specific with file references
    for _ in range(5):
        g = software_graph("small")
        nodes, proj = g[0], g[1]
        files = ["README.md", "package.json", "src/index.ts", "docker-compose.yml", "tsconfig.json"]
        f = pick(files)
        messages = [
            f"What's in {f}?",
            f"Show me the contents of {f}.",
            f"What does {f} configure?",
            f"¿Qué hay en {f}?",
        ]
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development", None, pick(messages), output
        ))

    return examples[:25]


def gen_intent_chat():
    """Generate chat intent examples."""
    examples = []

    # Simple acknowledgments
    simple_chat = [
        "Thanks!", "Thank you!", "Gracias!", "Got it.", "Ok.", "Understood.",
        "Cool.", "Nice!", "Great.", "Perfect.", "Perfecto.", "Dale.",
        "Genial.", "Buenísimo.", "Sure.", "Right.", "Yeah.",
        "I see.", "Noted.", "Ahh ok.", "Lol.", "Haha.", "Jaja.",
        "Good morning!", "Hey!", "Hello.", "Hola!",
    ]
    for msg in simple_chat[:15]:
        # Some with graph context, some without
        if random.random() < 0.5:
            g = software_graph("small")
            nodes = g[0]
            topic = f"{g[1][1]} development"
            prev = f"Here's what I found about {g[1][1]}."
        else:
            nodes = []
            topic = None
            prev = None
        output = v2_output("chat", "summary_only")
        examples.append(make_v2_example(nodes, pick_hint("same"), topic, prev, msg, output))

    # Opinions and reactions
    opinions = [
        "I think React is better than Vue for this.",
        "That's a really elegant solution.",
        "Me parece que eso está bien.",
        "I'm not sure about that approach.",
        "These are great stories.",
        "That's interesting.",
        "The weather is nice today.",
        "I prefer the functional approach.",
        "Creo que deberíamos repensar esto.",
        "This project is exciting!",
    ]
    for msg in opinions:
        g = software_graph("small") if random.random() < 0.5 else literature_graph(size="small")
        nodes = g[0]
        output = v2_output("chat", "summary_only")
        prev = "I've analyzed the project structure." if random.random() < 0.5 else None
        examples.append(make_v2_example(
            nodes, pick_hint("same"), "General", prev, msg, output
        ))

    return examples[:25]


def gen_intent_followup():
    """Generate followup intent examples."""
    examples = []

    # Software followups
    for _ in range(8):
        g = software_graph("medium")
        nodes, proj = g[0], g[1]
        tech = pick(FRONTEND + BACKEND + DATABASES)

        prev_responses = [
            f"{proj[1]} uses {tech[1]} for the main application logic.",
            f"The project has three main modules: auth, dashboard, and API.",
            f"The team consists of 5 developers working on {proj[1]}.",
        ]
        messages_en = [
            "Tell me more about that.",
            "Can you go deeper on this?",
            "What else should I know?",
            "Expand on the architecture.",
            "And what about the testing strategy?",
            "How does that connect to the frontend?",
            "What about performance?",
            "Any more details on that?",
        ]
        messages_es = [
            "Contame más sobre eso.",
            "¿Podés profundizar?",
            "¿Qué más debería saber?",
            "¿Y qué hay del testing?",
            "Expandí sobre la arquitectura.",
        ]

        msg = pick(messages_es) if spanish_chance() else pick(messages_en)
        output = v2_output("followup", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            pick(prev_responses), msg, output
        ))

    # Literature followups
    for _ in range(5):
        g = literature_graph(size="small")
        nodes, chars, places, title = g[0], g[1], g[2], g[3]
        char = pick(chars)

        prev = f"{char[1]} is a key character in {title}."
        messages = [
            "Tell me more about them.",
            "What happens to them next?",
            "And the other characters?",
            "¿Qué más sabés de ese personaje?",
            "Go on.",
        ]
        output = v2_output("followup", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), title, prev, pick(messages), output
        ))

    # Followup with info addition (user adds facts while continuing)
    for _ in range(5):
        g = software_graph("small")
        nodes, proj, org = g[0], g[1], g[2]
        person = pick(PERSONS)
        tech = pick(LANGUAGES)

        prev = f"{proj[1]} is being built at {org[1]}."
        messages = [
            f"Also, {person[1]} just joined as tech lead.",
            f"Oh, and we're adding {tech[1]} to the stack.",
            f"By the way, we just hit 10k users.",
            f"Ah, me olvidé — {person[1]} arrancó la semana pasada.",
        ]
        msg = pick(messages)

        # These have actual extraction
        if person[1] in msg:
            ents = [node(person[0], person[1], "person", "PERSONAL")]
            rels = [rel(person[0], proj[0], "maintains")]
        elif tech[1] in msg:
            ents = [node(tech[0], tech[1], "technology", "UNIVERSAL")]
            rels = [rel(proj[0], tech[0], "uses_technology")]
        else:
            ents = []
            rels = []
            facts_list = [fact_entry(proj[0], "Reached 10k users", "user")]

        output = v2_output(
            "followup", "with_chunks",
            entities=ents, relations=rels,
            facts=facts_list if not ents else [],
        )
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development", prev, msg, output
        ))

    return examples[:25]


# ═══════════════════════════════════════════════════════════════════════════
# B. Retrieval Decision Examples (~80)
# ═══════════════════════════════════════════════════════════════════════════

def gen_retrieval_summary_only():
    """Examples where summary_only is the correct retrieval."""
    examples = []

    # Conceptual questions
    conceptual_messages = [
        ("What is machine learning?", "overview"),
        ("Explain the repository pattern.", "overview"),
        ("What's the difference between SQL and NoSQL?", "overview"),
        ("¿Qué es la programación funcional?", "overview"),
        ("How does OAuth work conceptually?", "overview"),
        ("What are microservices?", "overview"),
        ("Explain dependency injection.", "overview"),
        ("¿Cuál es la diferencia entre REST y GraphQL?", "overview"),
    ]
    for msg, intent in conceptual_messages:
        g = software_graph("small")
        output = v2_output(intent, "summary_only")
        examples.append(make_v2_example(
            g[0], pick_hint("same"), f"{g[1][1]} development", None, msg, output
        ))

    # Relationship questions
    for _ in range(8):
        g = software_graph("medium")
        nodes, proj = g[0], g[1]
        people = g[6]
        if len(people) >= 2:
            messages = [
                f"Who works on {proj[1]}?",
                f"How does {people[0][1]} relate to {proj[1]}?",
                f"What's {people[0][1]}'s role in the team?",
                f"¿Quién trabaja en {proj[1]}?",
            ]
        else:
            messages = [
                f"Who's involved in {proj[1]}?",
                f"What's the team structure?",
            ]
        output = v2_output("specific", "summary_only")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development", None, pick(messages), output
        ))

    # Status/overview questions
    for _ in range(8):
        g = business_graph("medium")
        nodes, org = g[0], g[1]
        messages = [
            f"How's {org[1]} doing?",
            f"What's the current status?",
            f"¿Cómo va todo en {org[1]}?",
            f"Any updates on the project?",
            f"What's the team been working on?",
        ]
        output = v2_output("overview", "summary_only")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{org[1]} team", None, pick(messages), output
        ))

    # Chat (always summary_only)
    for _ in range(8):
        g = software_graph("small")
        nodes = g[0]
        messages = [
            "Sounds good!", "That makes sense.", "I'll think about it.",
            "Good point.", "Interesting approach.", "Me parece bien.",
            "Let me consider that.", "Fair enough.",
        ]
        output = v2_output("chat", "summary_only")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{g[1][1]} development",
            "Here's what I suggest.", pick(messages), output
        ))

    # Followup that only needs summary
    for _ in range(8):
        g = software_graph("small")
        nodes, proj = g[0], g[1]
        messages = [
            "Why did the team choose that approach?",
            "What's the rationale behind that decision?",
            "¿Por qué eligieron esa tecnología?",
            "How does that compare to alternatives?",
        ]
        output = v2_output("followup", "summary_only")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            f"We use React and FastAPI for {proj[1]}.", pick(messages), output
        ))

    return examples[:40]


def gen_retrieval_with_chunks():
    """Examples where with_chunks is the correct retrieval."""
    examples = []

    # Code lookups
    for _ in range(10):
        g = software_graph("medium")
        nodes, proj = g[0], g[1]
        messages = [
            f"Show me the auth middleware code.",
            f"What's in the main controller?",
            f"Show me the database schema definition.",
            f"What does the config file look like?",
            f"How is the router set up?",
            f"¿Cómo está implementado el login?",
            f"Show me the test setup.",
            f"What's in the Dockerfile?",
            f"How are the API routes defined?",
            f"What validations does the user model have?",
        ]
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            None, pick(messages), output
        ))

    # Specific content from documents
    for _ in range(8):
        g = literature_graph(size="small")
        nodes, chars, places, title = g[0], g[1], g[2], g[3]
        char = pick(chars)
        messages = [
            f"What exactly does {char[1]} say in the first scene?",
            f"Quote the passage about {places[0][1]}.",
            f"What happens in chapter 3?",
            f"Read me the dialogue between {chars[0][1]} and {chars[1][1]}.",
            f"¿Qué dice exactamente {char[1]}?",
        ]
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), title, None, pick(messages), output
        ))

    # Date/number/precise fact questions
    for _ in range(8):
        g = business_graph("medium")
        nodes, org = g[0], g[1]
        people = g[2]
        messages = [
            f"What's the exact deadline for the project?",
            f"How many users does the platform have?",
            f"What's the budget for Q2?",
            f"When was {people[0][1]} hired?",
            f"¿Cuál es la fecha exacta del deadline?",
            f"What are the specific KPIs?",
            f"How much revenue did we make last quarter?",
            f"What's the exact error message?",
        ]
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{org[1]} team", None, pick(messages), output
        ))

    # File-specific questions
    for _ in range(8):
        g = software_graph("small")
        nodes, proj = g[0], g[1]
        files = ["README.md", "package.json", "docker-compose.yml", ".env.example", "tsconfig.json"]
        f = pick(files)
        messages = [
            f"What does {f} say about the setup?",
            f"Show me {f}.",
            f"What's configured in {f}?",
            f"Read {f} for me.",
        ]
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development", None, pick(messages), output
        ))

    # Followup needing chunks
    for _ in range(6):
        g = software_graph("medium")
        nodes, proj = g[0], g[1]
        messages = [
            "Show me the actual implementation.",
            "Can I see the code for that?",
            "What exactly does it look like?",
            "¿Puedo ver el código?",
            "Go deeper into the implementation details.",
            "Show me the specific configuration.",
        ]
        output = v2_output("followup", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            f"The auth module uses JWT tokens with a 24-hour expiry.", pick(messages), output
        ))

    return examples[:40]


# ═══════════════════════════════════════════════════════════════════════════
# C. Code Extraction Examples (~50)
# ═══════════════════════════════════════════════════════════════════════════

def gen_code_extraction():
    """Generate examples where input is code and entities must be extracted."""
    examples = []

    # Code snippets with entities
    for snippet in CODE_SNIPPETS:
        proj = pick(PROJECTS)
        proj_node = existing_node(proj[0], proj[1], "project", "PERSONAL")
        nodes = [proj_node]

        # Add some existing tech nodes
        existing_tech = pick_n(FRONTEND + BACKEND + DATABASES, 2)
        for t in existing_tech:
            nodes.append(existing_node(t[0], t[1], "technology", "UNIVERSAL"))

        msg = f"Here's some {snippet['language']} code from {proj[1]}:\n\n```{snippet['language'].lower()}\n{snippet['code']}\n```"

        entities = []
        for eid, elabel, etype, elayer in snippet["entities"]:
            # Check if entity already exists in nodes
            if any(n["id"] == eid for n in nodes):
                entities.append(node(eid, elabel, etype, elayer, existing_id=eid))
            else:
                entities.append(node(eid, elabel, etype, elayer))

        rels = [rel(r[0], r[1], r[2]) for r in snippet["relations"]]
        # Add part_of relation to project
        for eid, _, etype, _ in snippet["entities"]:
            if etype == "concept":
                rels.append(rel(eid, proj[0], "part_of"))

        output = v2_output("specific", "with_chunks", entities=entities, relations=rels)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            None, msg, output
        ))

    # Code snippets described in conversation (not pasted)
    for _ in range(10):
        g = software_graph("medium")
        nodes, proj, org = g[0], g[1], g[2]
        fe, be = g[3], g[4]

        descriptions = [
            f"The {proj[1]} codebase uses a service layer pattern. Each domain has its own service class that handles business logic.",
            f"We have a middleware chain in {proj[1]}: auth → rate-limit → logging → handler.",
            f"The frontend uses a custom hook pattern. Every API call goes through useApi() which handles caching and errors.",
            f"Our CI/CD pipeline runs: lint → test → build → deploy. It's configured in GitHub Actions.",
            f"The database layer uses the repository pattern. Each table has a repository class with CRUD methods.",
            f"En {proj[1]} usamos inyección de dependencias. Cada servicio recibe sus dependencias en el constructor.",
            f"The API follows REST conventions. Resources are nested: /projects/{{id}}/tasks/{{taskId}}.",
            f"We use event sourcing for the audit log. Every state change emits a domain event.",
            f"The testing strategy is: unit tests for business logic, integration tests for API endpoints, e2e tests for critical flows.",
            f"Authentication uses refresh tokens stored in httpOnly cookies and short-lived JWTs in memory.",
        ]

        msg = pick(descriptions)
        pattern_name = msg.split(".")[0].split("uses")[-1].strip() if "uses" in msg else "Architecture Pattern"
        concept_id = _id(pattern_name)[:30]

        entities = [node(concept_id, pattern_name.title()[:40], "concept", "PERSONAL")]
        rels = [rel(concept_id, proj[0], "part_of")]

        output = v2_output("specific", "with_chunks", entities=entities, relations=rels)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            None, msg, output
        ))

    # Import statements
    for _ in range(8):
        g = software_graph("small")
        nodes, proj = g[0], g[1]
        techs = pick_n(FRONTEND + BACKEND + LANGUAGES + CSS_FW, 3)

        import_code = "\n".join([
            f"import {{ something }} from '{t[1].lower().replace(' ', '-')}';" for t in techs
        ])
        msg = f"Here are the imports from the main file:\n\n```typescript\n{import_code}\n```"

        entities = []
        rels = []
        for t in techs:
            if not any(n["id"] == t[0] for n in nodes):
                entities.append(node(t[0], t[1], "technology", "UNIVERSAL"))
            rels.append(rel(proj[0], t[0], "uses_technology"))

        output = v2_output("specific", "with_chunks", entities=entities, relations=rels)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            None, msg, output
        ))

    # Empty extraction from utility code
    for snippet in EMPTY_CODE_SNIPPETS:
        proj = pick(PROJECTS)
        nodes = [existing_node(proj[0], proj[1], "project", "PERSONAL")]
        msg = f"Here's some utility code:\n\n```{snippet['language'].lower()}\n{snippet['code']}\n```"
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            None, msg, output
        ))

    return examples[:50]


# ═══════════════════════════════════════════════════════════════════════════
# D. Literature/Prose Extraction (~40)
# ═══════════════════════════════════════════════════════════════════════════

def gen_prose_extraction():
    """Generate examples with prose/literature input for entity extraction."""
    examples = []

    # From PROSE_PASSAGES pool
    for passage in PROSE_PASSAGES:
        # Some with existing graph context, some without
        if random.random() < 0.5:
            nodes = [existing_node(e[0], e[1], e[2], e[3]) for e in passage["entities"][:2]]
        else:
            nodes = []

        msg = passage["text"]
        entities = [node(e[0], e[1], e[2], e[3]) for e in passage["entities"]]
        # Mark existing entities
        for ent in entities:
            if any(n["id"] == ent["id"] for n in nodes):
                ent["existing_id"] = ent["id"]

        rels = [rel(r[0], r[1], r[2]) for r in passage["relations"]]
        facts = [fact_entry(f[0], f[1], f[2]) for f in passage.get("facts", [])]

        output = v2_output("specific", "with_chunks",
                           action="changed", label="Literature",
                           entities=entities, relations=rels, facts=facts)
        examples.append(make_v2_example(
            nodes, "unresolved — classify the topic yourself", None, None, msg, output
        ))

    # Generated literature examples with known universes
    for _ in range(15):
        ukey = pick(list(LIT_UNIVERSES.keys()))
        chars_pool, places_pool, title = LIT_UNIVERSES[ukey]
        chars = pick_n(chars_pool, random.randint(2, 3))
        place = pick(places_pool)

        scene_templates = [
            f"{chars[0][1]} arrived at {place[1]} just before dawn. {chars[1][1]} was already waiting, looking anxious.",
            f"The confrontation between {chars[0][1]} and {chars[1][1]} took place at {place[1]}. Neither was willing to back down.",
            f"At {place[1]}, {chars[0][1]} discovered a hidden passage. {chars[1][1]} had known about it all along.",
            f"{chars[0][1]} y {chars[1][1]} se encontraron en {place[1]}. Fue un momento decisivo.",
            f"While {chars[0][1]} explored {place[1]}, {chars[1][1]} stood guard at the entrance.",
        ]

        msg = pick(scene_templates)
        entities = [node(c[0], c[1], "person", "UNIVERSAL") for c in chars]
        entities.append(node(place[0], place[1], "place", "UNIVERSAL"))
        rels = [rel(c[0], place[0], "located_in") for c in chars]

        # Some with existing context
        existing = [existing_node(chars[0][0], chars[0][1], "person", "UNIVERSAL")] if random.random() < 0.5 else []
        if existing:
            entities[0]["existing_id"] = chars[0][0]

        output = v2_output("specific", "with_chunks",
                           action="same" if existing else "changed",
                           label=None if existing else title,
                           entities=entities, relations=rels)
        examples.append(make_v2_example(
            existing, pick_hint("same" if existing else "changed"),
            title if existing else None, None, msg, output
        ))

    # Indirect character references ("the detective" = Holmes)
    for _ in range(5):
        g = literature_graph(size="medium")
        nodes, chars, places, title = g[0], g[1], g[2], g[3]
        char = chars[0]

        indirect_refs = [
            (f"The protagonist faced a difficult choice at {places[0][1]}.", char),
            (f"The hero returned to {places[0][1]} after a long journey.", char),
            (f"El protagonista volvió a {places[0][1]}.", char),
        ]
        msg_template, referenced_char = pick(indirect_refs)
        # Empty extraction — indirect references are hard, model should be conservative
        output = v2_output("specific", "with_chunks",
                           facts=[fact_entry(referenced_char[0], msg_template, "user")])
        examples.append(make_v2_example(
            nodes, pick_hint("same"), title, None, msg_template, output
        ))

    # Passage with NO extractable entities (descriptions of scenery, atmosphere)
    atmosphere_passages = [
        "The sun set over the mountains, casting long shadows across the valley. The air was crisp and clear, carrying the scent of pine trees.",
        "Rain fell steadily against the windows. The old house creaked in the wind. Everything was gray and still.",
        "La noche era oscura y silenciosa. Ni una estrella brillaba en el cielo.",
    ]
    for msg in atmosphere_passages:
        g = literature_graph(size="small")
        output = v2_output("specific", "with_chunks")
        examples.append(make_v2_example(
            g[0], pick_hint("same"), g[3], None, msg, output
        ))

    return examples[:40]


# ═══════════════════════════════════════════════════════════════════════════
# E. Documentation Extraction (~40)
# ═══════════════════════════════════════════════════════════════════════════

def gen_doc_extraction():
    """Generate examples with documentation input for entity extraction."""
    examples = []

    # From DOC_PASSAGES pool
    for passage in DOC_PASSAGES:
        proj = pick(PROJECTS)
        people = pick_n(PERSONS, 3)
        proj_node = existing_node(proj[0], proj[1], "project", "PERSONAL")
        nodes = [proj_node]
        for p in people:
            nodes.append(existing_node(p[0], p[1], "person", "PERSONAL"))

        # Replace placeholder names with random ones
        msg = passage["text"]
        msg = msg.replace("Beacon", proj[1])
        msg = msg.replace("Alice Chen", people[0][1])
        msg = msg.replace("Bob Martinez", people[1][1])
        msg = msg.replace("Priya Sharma", people[2][1] if len(people) > 2 else people[0][1])

        entities = []
        for e in passage["entities"]:
            entities.append(node(e[0], e[1], e[2], e[3]))

        rels = []
        for r in passage["relations"]:
            src = r[0]
            tgt = proj[0] if r[1] == "beacon" else r[1]
            rels.append(rel(src, tgt, r[2]))

        facts = []
        for f in passage["facts"]:
            entity_id = f[0]
            if entity_id == "beacon":
                entity_id = proj[0]
            elif entity_id == "alice_chen":
                entity_id = people[0][0]
            elif entity_id == "bob_martinez":
                entity_id = people[1][0]
            elif entity_id == "priya_sharma":
                entity_id = people[2][0] if len(people) > 2 else people[0][0]
            text = f[1].replace("Beacon", proj[1])
            facts.append(fact_entry(entity_id, text, f[2]))

        output = v2_output("specific", "with_chunks",
                           entities=entities, relations=rels, facts=facts)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            None, msg, output
        ))

    # README-style documentation
    for _ in range(10):
        proj = pick(PROJECTS)
        fe = pick(FRONTEND)
        be = pick(BACKEND)
        db = pick(DATABASES)
        app_type = pick(APP_TYPES_EN)

        readme = f"""# {proj[1]}

{proj[1]} is a {app_type} built with {fe[1]} and {be[1]}.

## Tech Stack
- Frontend: {fe[1]}
- Backend: {be[1]}
- Database: {db[1]}

## Getting Started
1. Clone the repo
2. Run `npm install`
3. Copy `.env.example` to `.env`
4. Run `npm run dev`"""

        nodes = [existing_node(proj[0], proj[1], "project", "PERSONAL")]
        entities = [
            node(fe[0], fe[1], "technology", "UNIVERSAL"),
            node(be[0], be[1], "technology", "UNIVERSAL"),
            node(db[0], db[1], "technology", "UNIVERSAL"),
        ]
        rels = [
            rel(proj[0], fe[0], "uses_technology"),
            rel(proj[0], be[0], "uses_technology"),
            rel(proj[0], db[0], "uses_technology"),
        ]
        facts = [fact_entry(proj[0], f"Is a {app_type}", "user")]

        output = v2_output("specific", "with_chunks",
                           entities=entities, relations=rels, facts=facts)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            None, f"Here's the README:\n\n{readme}", output
        ))

    # Changelog entries
    for _ in range(8):
        proj = pick(PROJECTS)
        techs = pick_n(FRONTEND + BACKEND + DATABASES + INFRA, 2)
        person = pick(PERSONS)

        versions = ["1.0", "1.1", "2.0", "3.0", "0.9"]
        ver = pick(versions)
        features = [
            f"Added {techs[0][1]} integration",
            "Improved performance by 40%",
            "Fixed critical authentication bug",
            f"Migrated to {techs[1][1]}",
            "Added multi-language support",
        ]
        changelog = f"""## v{ver} — 2025-03-15

Changes:
- {pick(features)}
- {pick(features)}
- Contributor: {person[1]}"""

        nodes = [
            existing_node(proj[0], proj[1], "project", "PERSONAL"),
            existing_node(person[0], person[1], "person", "PERSONAL"),
        ]
        facts = [
            fact_entry(proj[0], f"Released v{ver} on 2025-03-15", "user"),
            fact_entry(person[0], f"Contributed to {proj[1]} v{ver}", "user"),
        ]
        output = v2_output("specific", "with_chunks", facts=facts)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            None, f"From the changelog:\n\n{changelog}", output
        ))

    # Issue descriptions
    for _ in range(8):
        proj = pick(PROJECTS)
        person = pick(PERSONS)
        techs = pick_n(BACKEND + DATABASES, 2)

        issue_templates = [
            f"Bug report: Login fails when using OAuth2 with Google. Affects {techs[0][1]} session handling. Assigned to {person[1]}. Priority: High.",
            f"Feature request: Add CSV export to the dashboard. Requested by the sales team. {person[1]} will handle the {techs[0][1]} implementation.",
            f"Tech debt: Migrate from {techs[0][1]} to {techs[1][1]}. Estimated effort: 2 sprints. Owner: {person[1]}.",
            f"Reporte de bug: El endpoint de {techs[0][1]} falla con datos grandes. Asignado a {person[1]}. Prioridad: Alta.",
        ]

        msg = pick(issue_templates)
        nodes = [
            existing_node(proj[0], proj[1], "project", "PERSONAL"),
            existing_node(person[0], person[1], "person", "PERSONAL"),
        ]
        facts = []
        if "Assigned to" in msg or "Asignado a" in msg:
            facts.append(fact_entry(person[0], f"Assigned to fix issue in {proj[1]}", "user"))

        output = v2_output("specific", "with_chunks", facts=facts)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            None, msg, output
        ))

    return examples[:40]


# ═══════════════════════════════════════════════════════════════════════════
# F. S1.5 Improvement — Assistant Response Extraction (~30)
# ═══════════════════════════════════════════════════════════════════════════

def gen_s15_improvement():
    """
    Generate examples where the assistant's previous response contains
    extractable information that should be captured.
    """
    examples = []

    # Assistant mentions a person
    for _ in range(8):
        g = software_graph("medium")
        nodes, proj = g[0], g[1]
        new_person = pick([p for p in PERSONS if not any(n["id"] == p[0] for n in nodes)])
        role = pick(JOB_TITLES)

        prev_assistant = f"{new_person[1]} is the {role} for {proj[1]}. She joined last month and has been working on the authentication module."
        user_msg = pick([
            "Got it, thanks for the info.",
            "Ok, noted.",
            "Interesting, I didn't know that.",
            "Dale, gracias por la info.",
        ])

        entities = [
            node(new_person[0], new_person[1], "person", "PERSONAL",
                 facts=[{"text": f"Is the {role} for {proj[1]}", "speaker": "assistant"},
                        {"text": "Joined last month", "speaker": "assistant"},
                        {"text": "Working on the authentication module", "speaker": "assistant"}])
        ]
        rels = [
            rel(new_person[0], proj[0], "maintains"),
        ]

        output = v2_output("chat", "summary_only", entities=entities, relations=rels)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            prev_assistant, user_msg, output
        ))

    # Assistant confirms a fact
    for _ in range(7):
        g = software_graph("small")
        nodes, proj, org = g[0], g[1], g[2]

        assistant_facts = [
            (f"Yes, {proj[1]} uses PostgreSQL for the main database and Redis for caching.",
             [(proj[0], f"Uses PostgreSQL as main database", "assistant"),
              (proj[0], f"Uses Redis for caching", "assistant")]),
            (f"The deadline for {proj[1]} is Q2 2025. The team needs to deliver the MVP by then.",
             [(proj[0], "Deadline is Q2 2025 for MVP delivery", "assistant")]),
            (f"According to the docs, {proj[1]} supports up to 10,000 concurrent users.",
             [(proj[0], "Supports up to 10,000 concurrent users", "assistant")]),
            (f"{proj[1]} was started in January 2024 as an internal tool for {org[1]}.",
             [(proj[0], f"Started in January 2024 as internal tool", "assistant")]),
        ]

        prev_text, fact_list = pick(assistant_facts)
        user_msg = pick(["That's good to know.", "Makes sense.", "Entendido.", "Ok, got it."])

        facts = [fact_entry(f[0], f[1], f[2]) for f in fact_list]
        output = v2_output("chat", "summary_only", facts=facts)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            prev_text, user_msg, output
        ))

    # Assistant provides analysis with technology mentions
    for _ in range(7):
        g = software_graph("medium")
        nodes, proj = g[0], g[1]
        new_tech = pick([t for t in LANGUAGES + INFRA if not any(n["id"] == t[0] for n in nodes)])

        prev_assistant = f"Based on the codebase, {proj[1]} also uses {new_tech[1]} for build tooling. The configuration is in the root directory."
        user_msg = pick([
            "Interesting, I missed that.",
            "Ah, didn't notice that.",
            "Good catch.",
            "Gracias, no lo había visto.",
        ])

        entities = [node(new_tech[0], new_tech[1], "technology", "UNIVERSAL")]
        rels = [rel(proj[0], new_tech[0], "uses_technology")]

        output = v2_output("chat", "summary_only", entities=entities, relations=rels)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), f"{proj[1]} development",
            prev_assistant, user_msg, output
        ))

    # User shares personal info, assistant responds, user confirms
    for _ in range(8):
        person = pick(PERSONS)
        city = pick(CITIES)
        hobby = pick(HOBBIES)

        nodes = [existing_node(person[0], person[1], "person", "PERSONAL")]
        prev_assistant = f"So you live in {city[1]} and enjoy {hobby}. That's a great city for {hobby}!"
        user_msg = pick([
            "Yeah, exactly!",
            "Sí, exacto.",
            "That's right.",
            "Yep, love it there.",
        ])

        entities = [
            node(city[0], city[1], "place", "UNIVERSAL"),
            node(_id(hobby), hobby.title(), "concept", "UNIVERSAL"),
        ]
        facts = [
            fact_entry(person[0], f"Lives in {city[1]}", "assistant"),
            fact_entry(person[0], f"Enjoys {hobby}", "assistant"),
        ]

        output = v2_output("chat", "summary_only", entities=entities, facts=facts)
        examples.append(make_v2_example(
            nodes, pick_hint("same"), "Personal life",
            prev_assistant, user_msg, output
        ))

    return examples[:30]


# ═══════════════════════════════════════════════════════════════════════════
# G. S1 Failure Variations (~50)
# ═══════════════════════════════════════════════════════════════════════════

def gen_failure_variations():
    """
    Generate variations of the 9 S1 failures from v0.4 benchmarks.
    Focus on the overview vs specific boundary.
    """
    examples = []

    # ── Pattern 1: "What is X about?" → overview (6 failures of this type) ──
    overview_templates = [
        "What is this {} about?",
        "What does this {} do?",
        "Describe this {}.",
        "Tell me about this {}.",
        "¿De qué se trata este {}?",
        "¿Qué hace este {}?",
        "Describime este {}.",
        "¿Qué es este {}?",
        "What's the purpose of this {}?",
        "Give me the gist of this {}.",
        "Can you summarize this {}?",
        "Dame un resumen de este {}.",
    ]
    subjects = ["project", "application", "codebase", "repository", "book", "document", "system", "tool"]

    for _ in range(18):
        template = pick(overview_templates)
        subject = pick(subjects)
        msg = template.format(subject)

        # Vary the graph context
        if random.random() < 0.5:
            g = software_graph("small")
            nodes = g[0]
            topic = f"{g[1][1]} development"
        else:
            g = literature_graph(size="small")
            nodes = g[0]
            topic = g[3]

        output = v2_output("overview", "summary_only")
        examples.append(make_v2_example(
            nodes, "unresolved — classify the topic yourself", topic if random.random() < 0.3 else None,
            None, msg, output
        ))

    # ── Pattern 2: "That's interesting" / "These are great" → chat ──
    chat_reactions = [
        "That's interesting.",
        "That's really cool.",
        "These are great stories.",
        "I love these characters.",
        "This is fascinating.",
        "Qué interesante.",
        "Eso está buenísimo.",
        "Me encanta esto.",
        "What a great project.",
        "These are amazing features.",
        "That's impressive work.",
        "Qué bueno está esto.",
        "Nice architecture.",
        "Beautiful code.",
        "Cool stuff.",
    ]

    for msg in chat_reactions:
        if random.random() < 0.5:
            g = software_graph("small")
            nodes = g[0]
            topic = f"{g[1][1]} development"
            prev = f"Here's an overview of {g[1][1]}."
        else:
            g = literature_graph(size="small")
            nodes = g[0]
            topic = g[3]
            prev = f"The story of {g[3]} is set in a fantastical world."

        output = v2_output("chat", "summary_only")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), topic, prev, msg, output
        ))

    # ── Pattern 3: "Thanks for the overview" → chat ──
    thanks_patterns = [
        "Thanks for the overview.",
        "Thank you for explaining.",
        "Gracias por el resumen.",
        "Thanks, that helps.",
        "Got it, thanks for the explanation.",
        "Gracias por la info.",
        "Thanks for walking me through that.",
        "Appreciated, thanks.",
    ]

    for msg in thanks_patterns:
        g = software_graph("small")
        nodes = g[0]
        topic = f"{g[1][1]} development"
        prev = f"{g[1][1]} is a dashboard application built with modern technologies."
        output = v2_output("chat", "summary_only")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), topic, prev, msg, output
        ))

    # ── Pattern 4: "What genre/category/type?" → overview ──
    classification_questions = [
        "What genre would you classify these?",
        "What category does this fall into?",
        "What type of project is this?",
        "¿Qué género es este libro?",
        "¿En qué categoría entra esto?",
        "How would you categorize this?",
        "What kind of application is this?",
        "¿Qué tipo de proyecto es?",
    ]

    for msg in classification_questions:
        if "genre" in msg.lower() or "libro" in msg.lower():
            g = literature_graph(size="small")
            nodes = g[0]
            topic = g[3]
            prev = f"The story features many characters across different locations."
        else:
            g = software_graph("small")
            nodes = g[0]
            topic = f"{g[1][1]} development"
            prev = f"{g[1][1]} has several key modules."

        output = v2_output("overview", "summary_only")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), topic, prev, msg, output
        ))

    # ── Pattern 5: "How are X organized?" → overview ──
    organization_questions = [
        "How are tests organized?",
        "How is the code structured?",
        "How are the files organized?",
        "¿Cómo está organizado el código?",
        "What's the folder structure?",
        "How are components organized?",
        "¿Cómo están organizados los tests?",
        "How is the project structured?",
    ]

    for msg in organization_questions[:5]:
        g = software_graph("medium")
        nodes = g[0]
        topic = f"{g[1][1]} development"
        output = v2_output("overview", "summary_only")
        examples.append(make_v2_example(
            nodes, pick_hint("same"), topic, None, msg, output
        ))

    return examples[:50]


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

GENERATORS = [
    ("Intent: overview", gen_intent_overview, 25),
    ("Intent: specific", gen_intent_specific, 25),
    ("Intent: chat", gen_intent_chat, 25),
    ("Intent: followup", gen_intent_followup, 25),
    ("Retrieval: summary_only", gen_retrieval_summary_only, 40),
    ("Retrieval: with_chunks", gen_retrieval_with_chunks, 40),
    ("Code extraction", gen_code_extraction, 50),
    ("Prose extraction", gen_prose_extraction, 40),
    ("Documentation extraction", gen_doc_extraction, 40),
    ("S1.5 improvement", gen_s15_improvement, 30),
    ("Failure variations", gen_failure_variations, 50),
]


def validate_example(example: dict) -> bool:
    """Validate a v2 training example."""
    try:
        assert len(example["messages"]) == 3
        assert example["messages"][0]["role"] == "system"
        assert example["messages"][1]["role"] == "user"
        assert example["messages"][2]["role"] == "assistant"
        raw = example["messages"][2]["content"]
        ok, result = validate_s1(raw)
        if not ok:
            print(f"  Schema error: {result}")
            return False
        return True
    except (json.JSONDecodeError, AssertionError, KeyError) as e:
        print(f"  Validation error: {e}")
        return False


def generate(seed: int = 42):
    """Generate all v2 training examples."""
    random.seed(seed)

    all_examples = []
    print("Generating v2 training examples...\n")

    for name, gen_fn, target in GENERATORS:
        try:
            examples = gen_fn()
            # Validate
            valid = [ex for ex in examples if validate_example(ex)]
            invalid = len(examples) - len(valid)
            all_examples.extend(valid)
            status = f"OK ({len(valid)}/{len(examples)})"
            if invalid:
                status += f" [{invalid} invalid]"
            print(f"  {name:30s}: {status}")
        except Exception as e:
            print(f"  {name:30s}: ERROR — {e}")
            import traceback
            traceback.print_exc()

    print(f"\nTotal valid examples: {len(all_examples)}")

    # Shuffle
    random.shuffle(all_examples)

    # Split: 90% train, 10% val
    val_size = max(1, len(all_examples) // 10)
    val_examples = all_examples[:val_size]
    train_examples = all_examples[val_size:]

    # Write
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_path = OUTPUT_DIR / "s1_v2_new_training.jsonl"
    with open(train_path, "w", encoding="utf-8") as f:
        for ex in train_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(train_examples)} training examples to {train_path}")

    val_path = OUTPUT_DIR / "s1_v2_new_validation.jsonl"
    with open(val_path, "w", encoding="utf-8") as f:
        for ex in val_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(val_examples)} validation examples to {val_path}")

    # Distribution stats
    print("\n--- Distribution Stats ---")
    from collections import Counter
    intents = Counter()
    retrievals = Counter()
    for ex in all_examples:
        output = json.loads(ex["messages"][2]["content"])
        intents[output["intent"]] += 1
        retrievals[output["retrieval"]] += 1

    total = len(all_examples)
    print("Intent distribution:")
    for intent, count in sorted(intents.items()):
        print(f"  {intent:12s}: {count:4d} ({count/total*100:.1f}%)")
    print("Retrieval distribution:")
    for ret, count in sorted(retrievals.items()):
        print(f"  {ret:14s}: {count:4d} ({count/total*100:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate v2 training data")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate(seed=args.seed)

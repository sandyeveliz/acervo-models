# Case Scenario: Proyecto Codigo

**Turns:** 50 | **Passed:** 7/50 (14%)
**Entity acc:** 56% | **Relation acc:** 38% | **Fact acc:** 0% | **Topic acc:** 100%
**Graph:** 36 nodes, 87 edges | **Time:** 362.3s

## Turn-by-turn

| Turn | Ent% | Rel% | Fact% | Nodes | Δn | ms | Status |
|------|------|------|-------|-------|----|----|--------|
| 1 | 100% | — | — | 2 | +2 | 6985 | ✓ |
| 2 | 83% | 83% | — | 7 | +5 | 10014 | ✗ |
| 3 | 100% | 100% | 0% | 8 | +1 | 8938 | ✗ |
| 4 | 0% | — | 0% | 9 | +1 | 8875 | ✗ |
| 5 | — | — | 0% | 13 | +4 | 8140 | ✗ |
| 6 | 0% | 0% | 0% | 13 | +0 | 6469 | ✗ |
| 7 | — | — | 0% | 13 | +0 | 7155 | ✗ |
| 8 | — | — | 0% | 13 | +0 | 8734 | ✗ |
| 9 | 100% | 100% | — | 14 | +1 | 6797 | ✓ |
| 10 | — | — | 0% | 14 | +0 | 7186 | ✗ |
| 11 | — | — | 0% | 14 | +0 | 6344 | ✗ |
| 12 | — | — | 0% | 14 | +0 | 6219 | ✗ |
| 13 | 0% | 0% | — | 14 | +0 | 5780 | ✗ |
| 14 | — | — | 0% | 15 | +1 | 6452 | ✗ |
| 15 | 100% | 100% | 0% | 16 | +1 | 6953 | ✗ |
| 16 | 33% | 0% | — | 16 | +0 | 7359 | ✗ |
| 17 | — | — | 0% | 16 | +0 | 6265 | ✗ |
| 18 | — | — | 0% | 16 | +0 | 5984 | ✗ |
| 19 | — | — | 0% | 17 | +1 | 6842 | ✗ |
| 20 | — | — | 0% | 17 | +0 | 6500 | ✗ |
| 21 | 0% | 0% | — | 18 | +1 | 6938 | ✗ |
| 22 | 100% | 0% | 0% | 19 | +1 | 6844 | ✗ |
| 23 | 0% | 0% | — | 19 | +0 | 6984 | ✗ |
| 24 | — | — | 0% | 20 | +1 | 9530 | ✗ |
| 25 | 0% | 0% | 0% | 20 | +0 | 10219 | ✗ |
| 26 | — | — | 0% | 20 | +0 | 6530 | ✗ |
| 27 | — | — | 0% | 21 | +1 | 7094 | ✗ |
| 28 | — | — | 0% | 21 | +0 | 5983 | ✗ |
| 29 | — | — | 0% | 21 | +0 | 5907 | ✗ |
| 30 | — | — | — | 21 | +0 | 5811 | ✓ |
| 31 | 100% | 100% | 0% | 22 | +1 | 7672 | ✗ |
| 32 | — | — | 0% | 22 | +0 | 6030 | ✗ |
| 33 | — | — | 0% | 23 | +1 | 9813 | ✗ |
| 34 | — | — | 0% | 23 | +0 | 5875 | ✗ |
| 35 | 100% | 0% | — | 25 | +2 | 10780 | ✗ |
| 36 | — | — | 0% | 25 | +0 | 5952 | ✗ |
| 37 | — | — | 0% | 28 | +3 | 8484 | ✗ |
| 38 | — | — | 0% | 32 | +4 | 9796 | ✗ |
| 39 | 100% | 100% | — | 33 | +1 | 7360 | ✓ |
| 40 | — | — | — | 33 | +0 | 5811 | ✓ |
| 41 | 100% | 100% | — | 34 | +1 | 7030 | ✓ |
| 42 | 0% | 0% | — | 34 | +0 | 6578 | ✗ |
| 43 | 0% | 0% | — | 34 | +0 | 6140 | ✗ |
| 44 | 100% | 0% | 0% | 36 | +2 | 7609 | ✗ |
| 45 | — | — | 0% | 36 | +0 | 10092 | ✗ |
| 46 | — | — | 0% | 36 | +0 | 6797 | ✗ |
| 47 | — | — | 0% | 36 | +0 | 5938 | ✗ |
| 48 | — | — | 0% | 36 | +0 | 6421 | ✗ |
| 49 | — | — | 0% | 36 | +0 | 6405 | ✗ |
| 50 | — | — | — | 36 | +0 | 5859 | ✓ |

## Entity Misses (training data candidates)

- **T2** `Stack: React con TypeScript para el frontend, Node.js con Ex` → missing: ['Node.js']
- **T4** `Inicializá el monorepo con Turborepo. El package.json root d` → missing: ['pnpm']
- **T6** `El schema de User: id (uuid), name, email (unique), password` → missing: ['bcrypt', 'JWT']
- **T13** `Validación con Zod. Cada endpoint tiene su schema de validac` → missing: ['Zod']
- **T16** `Ahora el frontend. Creá el proyecto React con Vite y TypeScr` → missing: ['Zustand', 'Tailwind CSS']
- **T21** `Creá el API client con Axios. Un archivo api.ts que configur` → missing: ['Axios']
- **T23** `Quiero agregar categorías con iconos. Usemos lucide-react pa` → missing: ['lucide-react']
- **T25** `CI/CD con GitHub Actions. Pipeline: lint → test → build → de` → missing: ['GitHub Actions']
- **T42** `Documentá la API con Swagger/OpenAPI. Cada endpoint document` → missing: ['Swagger/OpenAPI']
- **T43** `Quiero agregar avatares generados automáticamente. Cuando un` → missing: ['DiceBear']

## Relation Misses

- **T2** → missing: [['dividiapp', 'nodejs']]
- **T6** → missing: [['dividiapp', 'bcrypt'], ['dividiapp', 'jwt']]
- **T13** → missing: [['dividiapp', 'zod']]
- **T16** → missing: [['dividiapp', 'vite'], ['dividiapp', 'zustand'], ['dividiapp', 'tailwind']]
- **T21** → missing: [['dividiapp', 'axios']]
- **T22** → missing: [['dividiapp', 'fcm']]
- **T23** → missing: [['dividiapp', 'lucide']]
- **T25** → missing: [['dividiapp', 'github_actions']]
- **T35** → missing: [['dividiapp', 'recharts']]
- **T42** → missing: [['dividiapp', 'swagger']]
- **T43** → missing: [['dividiapp', 'dicebear']]
- **T44** → missing: [['dividiapp', 'tesseract_js']]

## Fact Misses (training data candidates)

- **T3** `Empecemos con la estructura del proyecto. Quiero monorepo co` → missing: ['Estructura: monorepo Turborepo. apps/web (React), ']
- **T4** `Inicializá el monorepo con Turborepo. El package.json root d` → missing: ['Package manager: pnpm']
- **T5** `Ahora el backend. Necesito el modelo de datos. Las entidades` → missing: ['Modelo datos: User, Group, Expense, Settlement. Us']
- **T6** `El schema de User: id (uuid), name, email (unique), password` → missing: ['User schema: id uuid, name, email unique, password']
- **T7** `Schema de Group: id, name, description, created_by (FK user)` → missing: ['Group schema: id, name, description, created_by, i']
- **T8** `Schema de Expense: id, group_id, paid_by (FK user), amount (` → missing: ['Expense schema: group_id, paid_by, amount, descrip']
- **T10** `Ahora la API. Quiero endpoints REST con esta estructura: POS` → missing: ['API endpoints: auth (register/login), groups CRUD,']
- **T11** `El endpoint de balances es el más importante. El algoritmo t` → missing: ['Algoritmo balances: deudas netas + simplificación ']
- **T12** `Implementá el middleware de auth. Todas las rutas excepto /a` → missing: ['Auth middleware: JWT obligatorio excepto /auth/*. ']
- **T14** `Error handling centralizado. Necesito un error handler middl` → missing: ['Error handler centralizado: {error, message, code}']
- **T15** `Tests. Usemos Vitest para el backend. Quiero tests para: el ` → missing: ['Tests con Vitest: algoritmo balances, auth endpoin']
- **T17** `Páginas del frontend: Login, Register, Dashboard (lista de g` → missing: ['Páginas: Login, Register, Dashboard, GroupDetail, ']
- **T18** `El Dashboard muestra: tus grupos con el balance resumido de ` → missing: ['Dashboard: grupos con balance color-coded (verde=t']
- **T19** `GroupDetail tiene 3 tabs: Gastos (lista cronológica con quié` → missing: ['GroupDetail: 3 tabs - Gastos (cronológico), Balanc']
- **T20** `El form de AddExpense tiene: monto, descripción, categoría (` → missing: ['AddExpense form: monto, desc, categoría, fecha, sp']
- **T22** `Necesito notificaciones push. Vamos con Firebase Cloud Messa` → missing: ['Push notifications: FCM, trigger en nuevo gasto']
- **T24** `Ahora deploy. Configurá Railway con 2 servicios: api (Node.j` → missing: ['Deploy: API+DB en Railway, Frontend en Vercel. Env']
- **T25** `CI/CD con GitHub Actions. Pipeline: lint → test → build → de` → missing: ['CI/CD: PR=lint+test, merge main=deploy auto']
- **T26** `Necesito seed data para development. Creá un script que gene` → missing: ['Seed data: 3 users, 2 groups, 10 expenses con spli']
- **T27** `Implementá el dark mode. Tailwind tiene soporte nativo. Togg` → missing: ['Dark mode: toggle en Settings, persist localStorag']
- **T28** `Feature nueva: recurring expenses. Si pagás Netflix todos lo` → missing: ['Feature: gastos recurrentes con cron job backend']
- **T29** `Armá un README profesional. Badges de CI, features listados,` → missing: ['README: badges CI, features, screenshots, setup lo']
- **T31** `Quiero agregar internacionalización. i18next para React. Idi` → missing: ['i18n con i18next: español + inglés']
- **T32** `Feature: exportar gastos a CSV. Botón en GroupDetail que des` → missing: ['Feature: export gastos a CSV desde GroupDetail']
- **T33** `Necesito rate limiting en la API. Express-rate-limit, 100 re` → missing: ['Rate limiting: 100 req/min general, 5 req/min en l']
- **T34** `Agregá un endpoint GET /groups/:id/stats que devuelva: total` → missing: ['Endpoint stats: total gastado, promedio, top categ']
- **T36** `Security review. Verificá: SQL injection (Prisma debería pro` → missing: ['Security checklist: SQL injection, XSS, CSRF, CORS']
- **T37** `Performance: lazy loading de rutas con React.lazy(), code sp` → missing: ['Performance: lazy loading rutas, code splitting, p']
- **T38** `Vamos a agregar PWA support. Service worker para offline bás` → missing: ['PWA: service worker offline, manifest.json, instal']
- **T44** `Feature: receipts. Los usuarios pueden sacar foto del ticket` → missing: ['Feature: foto de ticket con OCR (Tesseract.js), ex']
- **T45** `Configurá environments: development (local), staging (Railwa` → missing: ['Environments: dev (local), staging (Railway previe']
- **T46** `El MVP está listo! Funcionalidades: auth, grupos con invite,` → missing: ['MVP v1.0.0 completo: auth, grupos, gastos, balance']
- **T47** `Mandé el link a mis amigos para que lo prueben. Creamos un g` → missing: ["Testing con amigos: grupo 'Asado del finde', funci"]
- **T48** `Feedback de los testers: quieren poder adjuntar fotos a los ` → missing: ['Feedback v1: adjuntar fotos a gastos, comentarios ']
- **T49** `Hacé un roadmap para v1.1: fotos en gastos, comentarios, mej` → missing: ['Roadmap v1.1: fotos, comentarios, UX improvements,']

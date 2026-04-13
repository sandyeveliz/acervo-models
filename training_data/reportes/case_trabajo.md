# Case Scenario: Trabajo

**Turns:** 50 | **Passed:** 7/50 (14%)
**Entity acc:** 78% | **Relation acc:** 43% | **Fact acc:** 4% | **Topic acc:** 100%
**Graph:** 32 nodes, 68 edges | **Time:** 434.1s

## Turn-by-turn

| Turn | Ent% | Rel% | Fact% | Nodes | Δn | ms | Status |
|------|------|------|-------|-------|----|----|--------|
| 1 | 100% | 50% | — | 9 | +9 | 11375 | ✗ |
| 2 | 100% | 0% | — | 11 | +2 | 9171 | ✗ |
| 3 | — | — | 0% | 11 | +0 | 6578 | ✗ |
| 4 | 50% | 0% | — | 12 | +1 | 8546 | ✗ |
| 5 | 100% | 50% | — | 14 | +2 | 9563 | ✗ |
| 6 | — | — | 0% | 14 | +0 | 6796 | ✗ |
| 7 | — | — | 0% | 15 | +1 | 6719 | ✗ |
| 8 | — | — | 0% | 15 | +0 | 5796 | ✗ |
| 9 | 100% | — | — | 18 | +3 | 8109 | ✓ |
| 10 | — | — | 0% | 18 | +0 | 7578 | ✗ |
| 11 | — | — | 0% | 19 | +1 | 7078 | ✗ |
| 12 | — | — | 0% | 19 | +0 | 7936 | ✗ |
| 13 | — | — | 0% | 19 | +0 | 7859 | ✗ |
| 14 | 0% | — | 0% | 19 | +0 | 8140 | ✗ |
| 15 | 100% | — | 0% | 20 | +1 | 8921 | ✗ |
| 16 | 100% | — | 0% | 21 | +1 | 7859 | ✗ |
| 17 | — | — | 0% | 22 | +1 | 11907 | ✗ |
| 18 | 100% | 100% | — | 23 | +1 | 10155 | ✓ |
| 19 | 100% | — | 0% | 25 | +2 | 8765 | ✗ |
| 20 | — | — | 0% | 26 | +1 | 8015 | ✗ |
| 21 | — | — | 0% | 26 | +0 | 8671 | ✗ |
| 22 | — | — | 0% | 27 | +1 | 9484 | ✗ |
| 23 | — | — | 0% | 27 | +0 | 6671 | ✗ |
| 24 | 100% | — | — | 28 | +1 | 6828 | ✓ |
| 25 | 100% | 100% | 100% | 29 | +1 | 8265 | ✓ |
| 26 | — | — | 0% | 29 | +0 | 7813 | ✗ |
| 27 | — | — | 0% | 29 | +0 | 8546 | ✗ |
| 28 | — | — | 0% | 29 | +0 | 8407 | ✗ |
| 29 | — | — | 0% | 29 | +0 | 7030 | ✗ |
| 30 | — | — | 0% | 30 | +1 | 7077 | ✗ |
| 31 | 0% | — | — | 30 | +0 | 8688 | ✗ |
| 32 | 100% | — | 0% | 31 | +1 | 6828 | ✗ |
| 33 | — | — | 50% | 31 | +0 | 12483 | ✗ |
| 34 | — | — | 0% | 31 | +0 | 6905 | ✗ |
| 35 | 0% | 0% | 0% | 31 | +0 | 15297 | ✗ |
| 36 | — | — | 0% | 31 | +0 | 34359 | ✗ |
| 37 | — | — | 0% | 31 | +0 | 6984 | ✗ |
| 38 | — | — | 0% | 31 | +0 | 6608 | ✗ |
| 39 | — | — | 0% | 31 | +0 | 7985 | ✗ |
| 40 | — | — | — | 31 | +0 | 6030 | ✓ |
| 41 | — | — | 0% | 31 | +0 | 7577 | ✗ |
| 42 | — | — | 0% | 31 | +0 | 7141 | ✗ |
| 43 | 100% | — | — | 32 | +1 | 9186 | ✓ |
| 44 | — | — | 0% | 32 | +0 | 6655 | ✗ |
| 45 | — | — | 0% | 32 | +0 | 6671 | ✗ |
| 46 | — | — | 0% | 32 | +0 | 9547 | ✗ |
| 47 | — | — | 0% | 32 | +0 | 7405 | ✗ |
| 48 | — | — | — | 32 | +0 | 5890 | ✓ |
| 49 | — | — | 0% | 32 | +0 | 9264 | ✗ |
| 50 | — | — | 0% | 32 | +0 | 6907 | ✗ |

## Entity Misses (training data candidates)

- **T4** `Checkear es para la empresa Inspecciones del Sur SRL. El con` → missing: ['Roberto Méndez']
- **T14** `Daniela de Butaco está re contenta, el e-commerce ya tiene 1` → missing: ['Mercado Pago', 'Andreani']
- **T31** `Entrevisté a Camila, backend dev de Cipolletti, 4 años de ex` → missing: ['Camila']
- **T35** `Camila implementó el OCR con Tesseract para Checkear. Lee la` → missing: ['Tesseract']

## Relation Misses

- **T1** → missing: [['altovallestudio', 'walletfy'], ['altovallestudio', 'checkear'], ['altovallestudio', 'butaco'], ['butaco', 'nextjs']]
- **T2** → missing: [['martin_dev', 'walletfy'], ['sofia_ux', 'walletfy']]
- **T4** → missing: [['roberto_mendez', 'inspecciones_del_sur'], ['inspecciones_del_sur', 'checkear']]
- **T5** → missing: [['daniela_ruiz', 'butaco_indumentaria']]
- **T35** → missing: [['checkear', 'tesseract']]

## Fact Misses (training data candidates)

- **T3** `Walletfy ya tiene beta con 20 usuarios. El feedback es posit` → missing: ['Beta con 20 usuarios. Feedback: más categorías + c']
- **T6** `Cobros este mes: Checkear me pagó 800.000 ARS. Butaco paga 6` → missing: ['Ingreso mensual: 800.000 ARS', 'Ingreso mensual: 600.000 ARS', 'Sin ingresos todavía']
- **T7** `Problema: Martín me avisa que se va en 2 meses. Le ofreciero` → missing: ['Se va en 2 meses, aceptó oferta en Globant']
- **T8** `Publiqué la búsqueda en LinkedIn y en la comunidad de devs d` → missing: ['Búsqueda: React dev con exp fintech, 2.5M ARS, ful']
- **T10** `Entrevisté a Lucas. Muy bueno técnicamente, conoce React y S` → missing: ['Entrevista positiva, conoce React + Supabase, ofer']
- **T11** `Lucas aceptó! Arranca el 1ro del mes que viene. Martín va a ` → missing: ['Aceptó, arranca el 1ro. Handoff 2 semanas con Mart']
- **T12** `Roberto de Inspecciones del Sur pidió una feature nueva para` → missing: ['Feature request: fotos con geolocalización automát']
- **T13** `Estimé 3 sprints de 2 semanas para la feature de fotos. Le p` → missing: ['Feature fotos: 3 sprints (6 sem), presupuesto 1.2M']
- **T14** `Daniela de Butaco está re contenta, el e-commerce ya tiene 1` → missing: ['Primer mes: 150 productos, 45 pedidos. Integrar Me']
- **T15** `Sofía hizo los mockups de la nueva UI de Walletfy. Está usan` → missing: ['Nuevos mockups: dashboard gastos con gráficos tort']
- **T16** `Necesitamos CI/CD para los 3 proyectos. Estoy configurando G` → missing: ['Falta CI/CD con GitHub Actions', 'Falta CI/CD con GitHub Actions']
- **T17** `Lucas arrancó hoy. Le di acceso al repo de Walletfy, al Supa` → missing: ['Primer día. Acceso repo + Supabase + Slack. Handof']
- **T19** `Problema en Butaco: el hosting en Vercel nos está saliendo c` → missing: ['Hosting Vercel: 75 USD/mes, demasiado caro. Evalua']
- **T20** `Reunión con Roberto. Aprobó el presupuesto de fotos. Empezam` → missing: ['Presupuesto fotos aprobado, arranca próxima semana']
- **T21** `Lucas está volando con Walletfy. En una semana implementó la` → missing: ['Implementó integración Fintoc en 1 semana', 'Feature: listing de cuentas bancarias via Fintoc']
- **T22** `Martín se fue hoy. Último día. Le armamos una despedida por ` → missing: ['Último día, handoff completado']
- **T23** `Walletfy beta update: 45 usuarios ahora (de 20). La conexión` → missing: ['Beta: 45 usuarios (+25). 80% conectaron cuenta ban']
- **T26** `Sofía diseñó el tema white-label de Walletfy. Permite cambia` → missing: ['White-label: customización colores/logo/nombre. Es']
- **T27** `Migré Butaco de Vercel a DigitalOcean. VPS de 12 USD/mes vs ` → missing: ['Migrado a DigitalOcean: 12 USD/mes (era 75 en Verc']
- **T28** `Sprint review de Checkear: feature de fotos terminada! Los i` → missing: ['Feature fotos con geolocalización: completada y pr']
- **T29** `Ingresos del mes: Checkear 800K + extra feature 400K = 1.2M,` → missing: ['Ingresos mes: Checkear 1.2M + Butaco 600K = 1.8M A']
- **T30** `Necesito contratar a alguien más. Un backend developer para ` → missing: ['Búsqueda: backend dev Node.js para Checkear + OCR']
- **T32** `Camila aceptó! Arranca la semana que viene. El equipo de Alt` → missing: ['Equipo: Sandy (lead), Lucas (Walletfy), Sofía (UX)']
- **T33** `CoinPay firmó contrato! 5.000 USD de setup fee ya cobrados. ` → missing: ['Primer cliente B2B: CoinPay']
- **T34** `Butaco superó los 100 pedidos mensuales! Daniela quiere suma` → missing: ['100+ pedidos/mes. Sumar calzado, filtros por talle']
- **T35** `Camila implementó el OCR con Tesseract para Checkear. Lee la` → missing: ['OCR con Tesseract: 85% precisión en etiquetas de m']
- **T36** `Estoy pensando en cobrar un retainer mensual a CoinPay por m` → missing: ['Retainer mantenimiento: 500 USD/mes (aceptado)']
- **T37** `Walletfy va a salir al app store la semana que viene! Versió` → missing: ['Launch v1.0 app store próxima semana. Free + premi']
- **T38** `WALLETFY ESTÁ EN EL APP STORE!!! 🎉 Primeras 24 horas: 150 de` → missing: ['Lanzamiento: 150 descargas en 24h, 12 premium (4.9']
- **T39** `Review de fin de trimestre de AltoValleStudio. Ingresos: Che` → missing: ['Q review: ingresos ~2.1M ARS/mes + ~560 USD/mes. E']
- **T41** `Roberto quiere un contrato anual para Checkear. 700K ARS/mes` → missing: ['Propuesta contrato anual: 700K ARS/mes fijos con s']
- **T42** `Acepté el contrato anual de Checkear. Firmamos por 12 meses.` → missing: ['Contrato anual firmado: 700K ARS/mes x 12 meses']
- **T44** `Empiezo a pensar que Butaco podría ser una plataforma SaaS d` → missing: ['Idea: pivotar a SaaS e-commerce para comercios loc']
- **T45** `Hablé con Daniela y le encanta la idea. Dice que ella puede ` → missing: ['Acepta ser referencia de Butaco SaaS con 50% descu']
- **T46** `Lucas implementó el white-label de Walletfy para CoinPay. Ya` → missing: ['White-label en producción, 200 usuarios activos se']
- **T47** `Walletfy en el app store: después de 1 mes, 1.200 descargas,` → missing: ['Mes 1 app store: 1.200 descargas, 85 premium, 4.6★']
- **T49** `Sofía propone hacer un redesign completo de Checkear. El fro` → missing: ['Propuesta: redesign y migración de Angular a React']
- **T50** `Resumen: AltoValleStudio pasó de ser yo solo haciendo freela` → missing: ['Evolución: de freelance solo a equipo de 4 con 3 p']

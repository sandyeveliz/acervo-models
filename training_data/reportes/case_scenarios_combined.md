# Case Scenarios — Combined Report (v0.6.0)

**Cases:** 8 | **Turns:** 397 | **Passed:** 63/397 (16%)
**Entity acc:** 61% | **Relation acc:** 24% | **Fact acc:** 6%

## Per-case breakdown

| Case | Domain | Turns | Pass% | Ent% | Rel% | Fact% | Topic% | Graph | Time |
|------|--------|-------|-------|------|------|-------|--------|-------|------|
| casa | Casa | 49 | 12% | 62% | 0% | 0% | 100% | 34n/61e | 368.4s |
| finanzas | Finanzas | 49 | 27% | 40% | 0% | 0% | 100% | 23n/30e | 326.2s |
| fitness | Fitness | 50 | 10% | 67% | 12% | 0% | 100% | 23n/39e | 374.3s |
| libro | Libro | 50 | 12% | 70% | 3% | 8% | 94% | 57n/130e | 413.6s |
| proyecto_codigo | Proyecto Codigo | 50 | 14% | 56% | 38% | 0% | 100% | 36n/87e | 362.3s |
| salud_familia | Salud Familia | 50 | 20% | 48% | 21% | 7% | 94% | 37n/72e | 371.2s |
| trabajo | Trabajo | 50 | 14% | 78% | 43% | 4% | 100% | 32n/68e | 434.1s |
| viajes | Viajes | 49 | 18% | 65% | 0% | 6% | 100% | 46n/92e | 363.8s |

## Training Data Candidates — Entity Misses (72 turns)

- **casa:T3** → ['Punto Sur Inmobiliaria', 'Lote La Herradura']
- **casa:T4** → ['Lote Puente 83']
- **casa:T6** → ['Carlos Peña']
- **casa:T8** → ['Casa La Herradura']
- **casa:T11** → ['Gabriela']
- **casa:T25** → ['Marmolería Del Sur']
- **casa:T32** → ['Néstor']
- **casa:T41** → ['Daniel']
- **finanzas:T4** → ['Fondo de Emergencia', 'Fondo Viaje 2027', 'Fondo Universidad Lionel', 'Fondo Jubilación', 'Fondo Casa Propia']
- **finanzas:T10** → ['Balanz Ahorro']
- **finanzas:T11** → ['Dólar MEP', 'AL30']
- **finanzas:T13** → ['CEDEARs']
- **finanzas:T14** → ['AAPL (CEDEAR)', 'MELI (CEDEAR)']
- **finanzas:T25** → ['TX26', 'TX28']
- **finanzas:T31** → ['Rocco']
- **finanzas:T35** → ['GOOGL (CEDEAR)', 'AMZN (CEDEAR)']
- **finanzas:T38** → ['Balanz Renta Fija']
- **fitness:T1** → ['Sandy']
- **fitness:T6** → ['Ezequiel Flores']
- **fitness:T29** → ['Media Maratón Neuquén']
- **fitness:T44** → ['Maratón Buenos Aires']
- **libro:T5** → ['Remedios la Bella']
- **libro:T6** → ['José Arcadio (hijo)', 'Amaranta Buendía']
- **libro:T10** → ['Aracataca']
- **libro:T19** → ['Último Aureliano']
- **libro:T24** → ['La Maga (Lucía)']
- **libro:T32** → ['Ernesto Sábato']
- **libro:T36** → ['Allende', 'Hunter']
- **libro:T40** → ['Ficciones', 'Jorge Luis Borges']
- **libro:T42** → ['El jardín de senderos que se bifurcan']
- ... and 42 more

## Training Data Candidates — Fact Misses (259 turns)

- **casa:T5** → ['Laura lo prefiere por cercanía a guarder', 'Sandy lo prefiere por espacio y tranquil']
- **casa:T7** → ['Comprado: seña 5.000 USD, saldo 27.000 U']
- **casa:T9** → ['Presupuesto llave en mano: 180.000 USD (']
- **casa:T10** → ['Costo total estimado: 240.000 USD (terre']
- **casa:T12** → ['Requisitos: 1 año antigüedad, ingresos 3', 'Califica para cuota hipotecaria de hasta']
- **casa:T13** → ['Estrategia: empezar con fondos propios, ']
- **casa:T15** → ['Plan 12 meses: M1-3 cimientos/estructura']
- **casa:T16** → ['Inicio de obra: movimiento de suelos y r']
- **casa:T18** → ['Problema: hierro subió 30%, necesidad de']
- **casa:T19** → ['Hierro comprado: 15.200 USD. Crédito nec']
- **casa:T20** → ['Pendiente: plano de gas para factibilida']
- **casa:T21** → ['Cimientos completados, arranca estructur', 'Descuento 10% por volumen']
- **casa:T22** → ['Problema: falta permiso de construcción ']
- **casa:T23** → ['Permiso de construcción aprobado, expedi']
- **casa:T24** → ['Pisos: porcelanato símil madera en zonas']
- **casa:T25** → ['Cocina: mesada granito negro. Baño princ']
- **casa:T26** → ['Mes 4: gastados 72K USD (12K sobre presu']
- **casa:T29** → ['Preinstalación solar en techo: 500 USD e']
- **casa:T30** → ['Crédito aprobado: 120K USD en UVA, 20 añ', 'Financiamiento: crédito hipotecario 120K']
- **casa:T31** → ['Estructura completa (columnas, vigas, lo']
- **casa:T33** → ['Aberturas: ventanas aluminio Modena Alua']
- **casa:T34** → ['Instalación de gas aprobada por Camuzzi,']
- **casa:T35** → ['Techo: chapa prepintada gris grafito + m']
- **casa:T36** → ['Mes 8/12: gastados 145K USD, disponible ']
- **casa:T37** → ['Jardín: sistema riego por goteo Netafim,']
- **casa:T38** → ['Dormitorio principal: sommier king size ']
- **casa:T39** → ['Dormitorio Lionel: temática astronautas,']
- **casa:T40** → ['Tercer dormitorio: oficina/estudio para ']
- **casa:T42** → ['Colores: living/cocina blanco cálido, do']
- **casa:T45** → ['Mes 11/12: casi terminada, gastados 195K']
- ... and 229 more

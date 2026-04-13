# Case Scenario: Casa

**Turns:** 49 | **Passed:** 6/49 (12%)
**Entity acc:** 62% | **Relation acc:** 0% | **Fact acc:** 0% | **Topic acc:** 100%
**Graph:** 34 nodes, 61 edges | **Time:** 368.4s

## Turn-by-turn

| Turn | Ent% | Rel% | Fact% | Nodes | Δn | ms | Status |
|------|------|------|-------|-------|----|----|--------|
| 1 | 100% | — | — | 1 | +1 | 9859 | ✓ |
| 2 | 100% | 0% | — | 4 | +3 | 7625 | ✗ |
| 3 | 33% | 0% | — | 6 | +2 | 9686 | ✗ |
| 4 | 0% | 0% | — | 6 | +0 | 6703 | ✗ |
| 5 | — | — | 0% | 6 | +0 | 5782 | ✗ |
| 6 | 0% | 0% | — | 7 | +1 | 8608 | ✗ |
| 7 | — | — | 0% | 7 | +0 | 6141 | ✗ |
| 8 | 0% | 0% | — | 8 | +1 | 7358 | ✗ |
| 9 | — | — | 0% | 8 | +0 | 8094 | ✗ |
| 10 | — | — | 0% | 8 | +0 | 6172 | ✗ |
| 11 | 50% | 0% | — | 9 | +1 | 9639 | ✗ |
| 12 | — | — | 0% | 9 | +0 | 5813 | ✗ |
| 13 | — | — | 0% | 9 | +0 | 6203 | ✗ |
| 14 | 100% | 0% | — | 11 | +2 | 8171 | ✗ |
| 15 | — | — | 0% | 11 | +0 | 6140 | ✗ |
| 16 | — | — | 0% | 11 | +0 | 7640 | ✗ |
| 17 | 100% | — | — | 15 | +4 | 9438 | ✓ |
| 18 | — | — | 0% | 15 | +0 | 6203 | ✗ |
| 19 | — | — | 0% | 15 | +0 | 6375 | ✗ |
| 20 | 100% | — | 0% | 17 | +2 | 7842 | ✗ |
| 21 | — | — | 0% | 17 | +0 | 7094 | ✗ |
| 22 | — | — | 0% | 18 | +1 | 8155 | ✗ |
| 23 | — | — | 0% | 18 | +0 | 6344 | ✗ |
| 24 | — | — | 0% | 19 | +1 | 6875 | ✗ |
| 25 | 0% | 0% | 0% | 21 | +2 | 9265 | ✗ |
| 26 | — | — | 0% | 21 | +0 | 7030 | ✗ |
| 27 | 100% | 0% | — | 22 | +1 | 7109 | ✗ |
| 28 | 100% | — | — | 23 | +1 | 7203 | ✓ |
| 29 | — | — | 0% | 23 | +0 | 7640 | ✗ |
| 30 | — | — | 0% | 24 | +1 | 8140 | ✗ |
| 31 | — | — | 0% | 24 | +0 | 6515 | ✗ |
| 32 | 0% | — | — | 24 | +0 | 7407 | ✗ |
| 33 | — | — | 0% | 24 | +0 | 12092 | ✗ |
| 34 | — | — | 0% | 24 | +0 | 8859 | ✗ |
| 35 | — | — | 0% | 25 | +1 | 7936 | ✗ |
| 36 | — | — | 0% | 25 | +0 | 7547 | ✗ |
| 37 | — | — | 0% | 26 | +1 | 6938 | ✗ |
| 38 | 100% | 0% | 0% | 28 | +2 | 8030 | ✗ |
| 39 | — | — | 0% | 29 | +1 | 8219 | ✗ |
| 40 | — | — | 0% | 29 | +0 | 6280 | ✗ |
| 41 | 0% | — | — | 30 | +1 | 7655 | ✗ |
| 42 | — | — | 0% | 31 | +1 | 7030 | ✗ |
| 43 | 100% | — | — | 32 | +1 | 7313 | ✓ |
| 44 | 100% | — | — | 33 | +1 | 7390 | ✓ |
| 45 | — | — | 0% | 33 | +0 | 7171 | ✗ |
| 46 | 100% | — | 0% | 34 | +1 | 7515 | ✗ |
| 47 | — | — | 0% | 34 | +0 | 7641 | ✗ |
| 48 | — | — | 0% | 34 | +0 | 6421 | ✗ |
| 49 | — | — | — | 34 | +0 | 6078 | ✓ |

## Entity Misses (training data candidates)

- **T3** `El inmobiliario Martín de la inmobiliaria Punto Sur nos most` → missing: ['Punto Sur Inmobiliaria', 'Lote La Herradura']
- **T4** `También vimos uno en Puente 83, 600m2 a 25.000 USD. No tiene` → missing: ['Lote Puente 83']
- **T6** `Fuimos a ver al arquitecto Carlos Peña. Tiene estudio en Neu` → missing: ['Carlos Peña']
- **T8** `Carlos Peña nos mostró el anteproyecto. Es una casa de 120m2` → missing: ['Casa La Herradura']
- **T11** `Fui al Banco Hipotecario a preguntar por el crédito UVA. Me ` → missing: ['Gabriela']
- **T25** `Para la cocina, Laura eligió mesada de granito negro de la m` → missing: ['Marmolería Del Sur']
- **T32** `Vecino del lote de al lado se presentó, se llama Néstor. Tam` → missing: ['Néstor']
- **T41** `El pintor arrancó esta semana. Se llama Daniel, recomendado ` → missing: ['Daniel']

## Relation Misses

- **T2** → missing: [['la_herradura', 'cipolletti'], ['puente_83', 'cipolletti']]
- **T3** → missing: [['martin_inmob', 'punto_sur'], ['lote_herradura', 'la_herradura']]
- **T4** → missing: [['lote_puente83', 'puente_83']]
- **T6** → missing: [['carlos_pena', 'neuquen']]
- **T8** → missing: [['carlos_pena', 'casa_proyecto']]
- **T11** → missing: [['gabriela_bh', 'banco_hipotecario']]
- **T14** → missing: [['jorge_dominguez', 'construir_srl']]
- **T25** → missing: [['del_sur', 'neuquen']]
- **T27** → missing: [['pablo_electricista', 'construir_srl']]
- **T38** → missing: [['muebles_sur', 'neuquen']]

## Fact Misses (training data candidates)

- **T5** `Laura prefiere La Herradura porque queda más cerca de la gua` → missing: ['Laura lo prefiere por cercanía a guardería y traba', 'Sandy lo prefiere por espacio y tranquilidad']
- **T7** `Decidimos ir con La Herradura! Señamos el lote con 5.000 USD` → missing: ['Comprado: seña 5.000 USD, saldo 27.000 USD en 6 cu']
- **T9** `El presupuesto de construcción que nos pasó Carlos es de 180` → missing: ['Presupuesto llave en mano: 180.000 USD (no incluye']
- **T10** `Entonces el total es: terreno 32.000 + proyecto 5.000 + cons` → missing: ['Costo total estimado: 240.000 USD (terreno 32K + p']
- **T12** `Los requisitos del crédito: antigüedad laboral 1 año, ingres` → missing: ['Requisitos: 1 año antigüedad, ingresos 3x cuota, s', 'Califica para cuota hipotecaria de hasta 1.2M ARS ']
- **T13** `Laura dice que empecemos a construir con lo que tenemos y de` → missing: ['Estrategia: empezar con fondos propios, crédito hi']
- **T15** `El plan de obra es: primeros 3 meses cimientos y estructura,` → missing: ['Plan 12 meses: M1-3 cimientos/estructura, M4-6 mam']
- **T16** `Empezó la obra!! Hoy vinieron a hacer el movimiento de suelo` → missing: ['Inicio de obra: movimiento de suelos y replanteo c']
- **T18** `Problema: el precio del hierro subió un 30% en un mes. Jorge` → missing: ['Problema: hierro subió 30%, necesidad de comprar 1']
- **T19** `Compramos todo el hierro, 15.200 USD. Nos queda justo para l` → missing: ['Hierro comprado: 15.200 USD. Crédito necesario ant']
- **T20** `La semana que viene viene el gasista Rubén a hacer el proyec` → missing: ['Pendiente: plano de gas para factibilidad de Camuz']
- **T21** `Los cimientos están listos! Jorge dice que quedaron perfecto` → missing: ['Cimientos completados, arranca estructura hormigón', 'Descuento 10% por volumen']
- **T22** `Tuvimos un problema con el municipio. Nos falta un permiso d` → missing: ['Problema: falta permiso de construcción municipal,']
- **T23** `Salió el permiso de construcción! Número de expediente 2847/` → missing: ['Permiso de construcción aprobado, expediente 2847/']
- **T24** `Laura quiere piso de porcelanato en toda la casa menos los d` → missing: ['Pisos: porcelanato símil madera en zonas comunes, ']
- **T25** `Para la cocina, Laura eligió mesada de granito negro de la m` → missing: ['Cocina: mesada granito negro. Baño principal: vani']
- **T26** `Vamos mes 4 de obra y llevamos gastados 72.000 USD. Nos pasa` → missing: ['Mes 4: gastados 72K USD (12K sobre presupuesto de ']
- **T29** `Carlos sugiere dejar la preinstalación para paneles solares ` → missing: ['Preinstalación solar en techo: 500 USD extra, reco']
- **T30** `Aprobamos el crédito hipotecario del Banco Hipotecario! 120.` → missing: ['Crédito aprobado: 120K USD en UVA, 20 años, cuota ', 'Financiamiento: crédito hipotecario 120K USD aprob']
- **T31** `La estructura está casi lista. Columnas, vigas y losa termin` → missing: ['Estructura completa (columnas, vigas, losa). Arran']
- **T33** `Eligiendo aberturas: ventanas de aluminio línea Modena de Al` → missing: ['Aberturas: ventanas aluminio Modena Aluar, puertas']
- **T34** `Rubén terminó la instalación de gas. Pasó la inspección de C` → missing: ['Instalación de gas aprobada por Camuzzi, medidor e']
- **T35** `El techo va con chapa y aislación térmica. Jorge sugiere mem` → missing: ['Techo: chapa prepintada gris grafito + membrana as']
- **T36** `Estamos en mes 8 de 12. Lleamos gastados 145.000 USD. Nos qu` → missing: ['Mes 8/12: gastados 145K USD, disponible 50K (35K c']
- **T37** `Para el jardín estoy pensando en riego por goteo automático.` → missing: ['Jardín: sistema riego por goteo Netafim, 2.000 USD']
- **T38** `Laura ya está viendo muebles en Muebles Sur de Neuquén y en ` → missing: ['Dormitorio principal: sommier king size + placard ']
- **T39** `El dormitorio de Lionel lo estamos pensando con tema de astr` → missing: ['Dormitorio Lionel: temática astronautas, cama Mont']
- **T40** `Falta el tercer dormitorio que por ahora va a ser oficina/es` → missing: ['Tercer dormitorio: oficina/estudio para trabajo re']
- **T42** `Los colores que eligió Laura: living y cocina blanco cálido,` → missing: ['Colores: living/cocina blanco cálido, dormitorio L']
- **T45** `La casa está casi terminada!!! Mes 11 de 12, faltan terminac` → missing: ['Mes 11/12: casi terminada, gastados 195K USD (15K ']
- **T46** `La mudanza la hacemos con Transportes Arias de Cipolletti. N` → missing: ['Mudanza programada para el 15 del mes que viene']
- **T47** `Cancelamos el alquiler con 30 días de preaviso como dice el ` → missing: ['Alquiler cancelado, depósito devuelto 700K ARS, de']
- **T48** `NOS MUDAMOS!!! 🎉 La casa quedó espectacular. Lionel ama su c` → missing: ['Mudanza completada. Casa terminada y habitada.']

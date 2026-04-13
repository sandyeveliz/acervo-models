# Case Scenario: Viajes

**Turns:** 49 | **Passed:** 9/49 (18%)
**Entity acc:** 65% | **Relation acc:** 0% | **Fact acc:** 6% | **Topic acc:** 100%
**Graph:** 46 nodes, 92 edges | **Time:** 363.8s

## Turn-by-turn

| Turn | Ent% | Rel% | Fact% | Nodes | Δn | ms | Status |
|------|------|------|-------|-------|----|----|--------|
| 1 | 0% | — | — | 2 | +2 | 7030 | ✗ |
| 2 | 0% | — | 0% | 2 | +0 | 6234 | ✗ |
| 3 | — | — | 0% | 2 | +0 | 6000 | ✗ |
| 4 | 0% | — | 0% | 2 | +0 | 7609 | ✗ |
| 5 | 100% | — | 0% | 6 | +4 | 8265 | ✗ |
| 6 | — | — | 0% | 6 | +0 | 5780 | ✗ |
| 7 | 0% | 0% | — | 8 | +2 | 7391 | ✗ |
| 8 | 100% | 0% | — | 13 | +5 | 10000 | ✗ |
| 9 | — | — | — | 13 | +0 | 5952 | ✓ |
| 10 | 100% | — | — | 16 | +3 | 8030 | ✓ |
| 11 | — | — | 0% | 16 | +0 | 5875 | ✗ |
| 12 | 0% | 0% | — | 16 | +0 | 7530 | ✗ |
| 13 | 100% | 0% | 0% | 16 | +0 | 8266 | ✗ |
| 14 | 0% | 0% | — | 17 | +1 | 7390 | ✗ |
| 15 | 100% | 0% | — | 19 | +2 | 7375 | ✗ |
| 16 | 0% | 0% | — | 22 | +3 | 9328 | ✗ |
| 17 | 100% | 0% | — | 25 | +3 | 9327 | ✗ |
| 18 | 100% | 0% | 0% | 26 | +1 | 9547 | ✗ |
| 19 | — | — | 0% | 27 | +1 | 8436 | ✗ |
| 20 | — | — | 0% | 27 | +0 | 7594 | ✗ |
| 21 | 100% | 0% | — | 29 | +2 | 9483 | ✗ |
| 22 | — | — | 100% | 29 | +0 | 7594 | ✓ |
| 23 | 100% | 0% | — | 31 | +2 | 8344 | ✗ |
| 24 | 100% | 0% | — | 33 | +2 | 7530 | ✗ |
| 25 | 100% | 0% | — | 34 | +1 | 6641 | ✗ |
| 26 | 100% | 0% | — | 36 | +2 | 7077 | ✗ |
| 27 | 100% | 0% | — | 37 | +1 | 7936 | ✗ |
| 28 | 100% | — | — | 38 | +1 | 7610 | ✓ |
| 29 | — | — | 0% | 38 | +0 | 6202 | ✗ |
| 30 | — | — | 0% | 38 | +0 | 6390 | ✗ |
| 31 | — | — | 0% | 38 | +0 | 6250 | ✗ |
| 32 | — | — | 0% | 38 | +0 | 6734 | ✗ |
| 33 | 0% | — | — | 38 | +0 | 5984 | ✗ |
| 34 | — | — | 0% | 39 | +1 | 7484 | ✗ |
| 35 | — | — | 0% | 39 | +0 | 8155 | ✗ |
| 36 | — | — | 0% | 40 | +1 | 7280 | ✗ |
| 37 | 100% | 0% | — | 41 | +1 | 6797 | ✗ |
| 38 | — | — | 0% | 41 | +0 | 5905 | ✗ |
| 39 | — | — | — | 41 | +0 | 6046 | ✓ |
| 40 | 0% | — | 0% | 41 | +0 | 6828 | ✗ |
| 41 | — | — | 50% | 42 | +1 | 7625 | ✗ |
| 42 | — | — | 0% | 42 | +0 | 7125 | ✗ |
| 43 | 100% | — | — | 43 | +1 | 7390 | ✓ |
| 44 | 100% | — | — | 44 | +1 | 7297 | ✓ |
| 45 | — | — | 0% | 45 | +1 | 9546 | ✗ |
| 46 | — | — | 0% | 46 | +1 | 8000 | ✗ |
| 47 | — | — | 0% | 46 | +0 | 8203 | ✗ |
| 48 | — | — | — | 46 | +0 | 7421 | ✓ |
| 49 | — | — | — | 46 | +0 | 5921 | ✓ |

## Entity Misses (training data candidates)

- **T1** `Quiero empezar a planificar el viaje a España para enero 202` → missing: ['Viaje España 2027', 'España']
- **T2** `La idea es Madrid una semana y Barcelona otra semana. Total ` → missing: ['Madrid', 'Barcelona']
- **T4** `Laura tiene ciudadanía italiana y ya le inició el trámite a ` → missing: ['Consulado Italiano Bahía Blanca']
- **T7** `Para alojamiento estoy viendo Airbnb. En Madrid un depto de ` → missing: ['Malasaña', 'Eixample']
- **T12** `Día 1 domingo: llegar, hacer check-in en el Airbnb, caminar ` → missing: ['Plaza Mayor']
- **T14** `Día 3: excursión a Toledo. Sale un tren AVE desde Atocha que` → missing: ['Estación Atocha']
- **T16** `Día 5: Palacio Real y Jardines de Sabatini a la mañana. A la` → missing: ['Palacio Real de Madrid']
- **T33** `Necesitamos seguro de viaje. Assist Card o Universal Assista` → missing: ['Assist Card', 'Universal Assistance']
- **T40** `Voy a llevar 500 EUR en efectivo y usar la tarjeta Prex para` → missing: ['Prex']

## Relation Misses

- **T7** → missing: [['malasana', 'madrid'], ['eixample', 'barcelona']]
- **T8** → missing: [['museo_prado', 'madrid'], ['sagrada_familia', 'barcelona'], ['park_guell', 'barcelona']]
- **T12** → missing: [['plaza_mayor', 'madrid']]
- **T13** → missing: [['retiro', 'madrid']]
- **T14** → missing: [['atocha', 'madrid']]
- **T15** → missing: [['chueca', 'madrid']]
- **T16** → missing: [['palacio_real', 'madrid']]
- **T17** → missing: [['meson_candido', 'segovia']]
- **T18** → missing: [['mercado_san_miguel', 'madrid']]
- **T21** → missing: [['las_ramblas', 'barcelona'], ['barrio_gotico', 'barcelona']]
- **T23** → missing: [['barceloneta', 'barcelona']]
- **T24** → missing: [['casa_batllo', 'barcelona'], ['la_pedrera', 'barcelona']]
- **T25** → missing: [['montjuic', 'barcelona']]
- **T26** → missing: [['boqueria', 'barcelona']]
- **T27** → missing: [['tibidabo', 'barcelona']]
- **T37** → missing: [['rodrigo', 'madrid']]

## Fact Misses (training data candidates)

- **T2** `La idea es Madrid una semana y Barcelona otra semana. Total ` → missing: ['Plan: Madrid 1 semana + Barcelona 1 semana = 15 dí']
- **T3** `¿Qué necesitamos para viajar con un bebé de 1 año y medio? D` → missing: ['Tiene pasaporte argentino, no tiene pasaporte ital']
- **T4** `Laura tiene ciudadanía italiana y ya le inició el trámite a ` → missing: ['Tiene ciudadanía italiana']
- **T5** `Vi vuelos en Google Flights. Buenos Aires - Madrid ida y vue` → missing: ['Vuelos BUE-MAD Iberia: ~1.200 USD/adulto + ~120 US']
- **T6** `Con 2.520 de vuelos nos quedan 2.480 USD para 15 días. Son u` → missing: ['Presupuesto diario: ~165 USD/día para 3 personas (']
- **T11** `Armemos un itinerario día por día para Madrid. Llegamos un d` → missing: ['Llegada a Madrid: domingo por la mañana']
- **T13** `Día 2 lunes: Museo del Prado a la mañana (la entrada con beb` → missing: ['Entrada gratis para bebés']
- **T18** `Día 7 sábado: último día en Madrid, Mercado de San Miguel pa` → missing: ['Madrid → Barcelona en AVE, 2h45']
- **T19** `Para Barcelona quiero reservar un depto en el Eixample. Enco` → missing: ['Airbnb Barcelona: Eixample, 85 EUR/noche con cuna,']
- **T20** `Reservé! Airbnb Madrid del 5 al 12 de enero (7 noches) y Bar` → missing: ['Alojamiento reservado: Madrid 5-12 ene, Barcelona ']
- **T29** `Entonces los vuelos quedan: ida Buenos Aires → Madrid con Ib` → missing: ['Vuelos totales: 4.725 USD (ida Iberia 2.520 + vuel']
- **T30** `Necesitamos subir el presupuesto a 7.000 USD mínimo. 4.725 v` → missing: ['Presupuesto revisado: 7.000 USD (vuelos 4.725 + al']
- **T31** `Laura dice que con 925 USD para gastos en 15 días no alcanza` → missing: ['Presupuesto final: 8.000 USD. Gastos diarios: ~110']
- **T32** `Para las comidas: desayuno en el depto, almuerzo menú del dí` → missing: ['Plan comida: desayuno en depto, almuerzo menú del ']
- **T34** `Contratamos Assist Card plan familiar. 150 USD los 15 días p` → missing: ['Seguro: Assist Card familiar, 150 USD/15 días, cob']
- **T35** `Lista de cosas que llevar para Lionel en el viaje: pañales p` → missing: ['Equipaje Lionel: pañales 3 días, comida, cochecito']
- **T36** `Ah, la Dra. Fernández me dijo que pidamos un certificado méd` → missing: ['Pendiente: certificado médico de viaje para Lionel']
- **T38** `Checklist del viaje: ✅ vuelos, ✅ alojamiento, ✅ seguro, ⬜ pa` → missing: ['Checklist: vuelos ✅, alojamiento ✅, seguro ✅. Pend']
- **T40** `Voy a llevar 500 EUR en efectivo y usar la tarjeta Prex para` → missing: ['Efectivo: 500 EUR + tarjeta Prex para resto']
- **T41** `Salió el pasaporte italiano de Lionel! Ahora tenemos los 3 p` → missing: ['Documentación: Laura y Lionel pasaporte italiano, ']
- **T42** `Reservé la Sagrada Familia para el 13 de enero a las 9am. Nú` → missing: ['Reserva 13 enero 9am, ref SGF-2027-45892, 52 EUR (']
- **T45** `Actualicemos el itinerario: sacamos un día libre y agregamos` → missing: ['Accesible con cochecito via cremallera según Fede']
- **T46** `El certificado médico de Lionel ya está listo. La Dra. Ferná` → missing: ['Certificado médico Lionel listo: bilingüe, alergia']
- **T47** `Presupuesto final final: vuelos 4.725 + alojamiento 1.350 + ` → missing: ['Presupuesto final: 8.000 USD. Ahorrados 3.200, fal', 'Progreso: 3.200 de 8.000 USD (40%)']

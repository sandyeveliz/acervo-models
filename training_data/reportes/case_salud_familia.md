# Case Scenario: Salud Familia

**Turns:** 50 | **Passed:** 10/50 (20%)
**Entity acc:** 48% | **Relation acc:** 21% | **Fact acc:** 7% | **Topic acc:** 94%
**Graph:** 37 nodes, 72 edges | **Time:** 371.2s

## Turn-by-turn

| Turn | Ent% | Rel% | Fact% | Nodes | Δn | ms | Status |
|------|------|------|-------|-------|----|----|--------|
| 1 | 100% | 100% | — | 3 | +3 | 7703 | ✓ |
| 2 | 50% | 100% | — | 4 | +1 | 6921 | ✗ |
| 3 | — | — | — | 4 | +0 | 5484 | ✓ |
| 4 | — | — | 33% | 4 | +0 | 7390 | ✗ |
| 5 | 0% | — | — | 4 | +0 | 6094 | ✗ |
| 6 | 0% | — | 0% | 5 | +1 | 6592 | ✗ |
| 7 | 100% | 100% | 0% | 6 | +1 | 7250 | ✗ |
| 8 | — | — | — | 6 | +0 | 5657 | ✓ |
| 9 | 100% | 0% | — | 7 | +1 | 7390 | ✗ |
| 10 | 100% | 0% | 0% | 8 | +1 | 8280 | ✗ |
| 11 | — | 100% | 0% | 8 | +0 | 6484 | ✗ |
| 12 | 50% | 0% | — | 9 | +1 | 8719 | ✗ |
| 13 | 0% | — | 0% | 9 | +0 | 7109 | ✗ |
| 14 | — | — | 0% | 9 | +0 | 5671 | ✗ |
| 15 | 0% | 0% | 0% | 9 | +0 | 7686 | ✗ |
| 16 | 0% | 0% | 0% | 11 | +2 | 9000 | ✗ |
| 17 | — | — | 0% | 13 | +2 | 7203 | ✗ |
| 18 | — | — | 0% | 13 | +0 | 7421 | ✗ |
| 19 | — | — | 0% | 13 | +0 | 7250 | ✗ |
| 20 | — | — | 0% | 13 | +0 | 6655 | ✗ |
| 21 | 0% | — | 0% | 13 | +0 | 7359 | ✗ |
| 22 | — | — | 0% | 14 | +1 | 7030 | ✗ |
| 23 | — | — | — | 14 | +0 | 5922 | ✓ |
| 24 | 100% | 0% | — | 16 | +2 | 7233 | ✗ |
| 25 | 50% | 0% | — | 17 | +1 | 6453 | ✗ |
| 26 | 100% | 0% | — | 19 | +2 | 11109 | ✗ |
| 27 | 0% | 0% | — | 20 | +1 | 7359 | ✗ |
| 28 | — | — | — | 20 | +0 | 6000 | ✓ |
| 29 | — | 0% | 50% | 20 | +0 | 7311 | ✗ |
| 30 | 100% | 0% | 0% | 21 | +1 | 8109 | ✗ |
| 31 | — | — | 100% | 21 | +0 | 7530 | ✓ |
| 32 | — | — | 0% | 21 | +0 | 7063 | ✗ |
| 33 | — | — | 0% | 22 | +1 | 7265 | ✗ |
| 34 | 50% | 0% | — | 23 | +1 | 7796 | ✗ |
| 35 | — | — | — | 23 | +0 | 5875 | ✓ |
| 36 | 100% | — | — | 24 | +1 | 8250 | ✗ |
| 37 | 0% | 0% | — | 26 | +2 | 8047 | ✗ |
| 38 | 0% | — | — | 26 | +0 | 7921 | ✗ |
| 39 | 50% | — | 0% | 28 | +2 | 9969 | ✗ |
| 40 | — | — | — | 28 | +0 | 5984 | ✓ |
| 41 | 50% | — | 0% | 29 | +1 | 7358 | ✗ |
| 42 | 100% | 0% | 0% | 31 | +2 | 9750 | ✗ |
| 43 | — | — | 0% | 31 | +0 | 7719 | ✗ |
| 44 | 0% | 0% | 0% | 32 | +1 | 8719 | ✗ |
| 45 | — | — | — | 32 | +0 | 5984 | ✓ |
| 46 | 100% | — | — | 35 | +3 | 9469 | ✗ |
| 47 | — | — | 0% | 35 | +0 | 8594 | ✗ |
| 48 | 0% | — | — | 35 | +0 | 7750 | ✗ |
| 49 | 50% | — | — | 37 | +2 | 8296 | ✗ |
| 50 | — | — | — | 37 | +0 | 6000 | ✓ |

## Entity Misses (training data candidates)

- **T2** `Lionel tiene turno con la pediatra Dra. Fernández el viernes` → missing: ['Turno pediatra viernes']
- **T5** `El próximo control es a los 9 meses, en julio. Ahí le toca l` → missing: ['Control 9 meses']
- **T6** `La doctora nos dijo que ya podemos empezar con alimentación ` → missing: ['BLW']
- **T12** `Laura tiene turno con la ginecóloga Dra. Martínez la semana ` → missing: ['Control post-parto Laura']
- **T13** `Tenemos OSDE 310, cubre bastante bien. Las consultas pediátr` → missing: ['OSDE 310']
- **T15** `Laura empezó kinesiología con Martín Sosa en la clínica Reba` → missing: ['Martín Sosa', 'Clínica Rebalance', 'Neuquén']
- **T16** `Lionel probó zapallo hoy por primera vez. Le encantó. Mañana` → missing: ['Baby-Led Weaning (libro)']
- **T21** `Lionel tiene fiebre, 38.5. Le dimos Ibueván gotas como nos d` → missing: ['Hospital Castro Rendón']
- **T25** `Mi hermano Diego dice que su hija Valentina de 3 años tuvo l` → missing: ['Diego']
- **T27** `Laura quiere anotarse en natación para mamás y bebés con Lio` → missing: ['Club Cipolletti']
- **T34** `Mi suegra Marta viene de Buenos Aires la semana que viene a ` → missing: ['Buenos Aires']
- **T37** `Vi un Fiat Cronos 2024 en la concesionaria Yacopini de Neuqu` → missing: ['Yacopini', 'Dietrich']
- **T38** `Laura prefiere el Virtus por el baúl más grande. Mi viejo Ra` → missing: ['Raúl']
- **T39** `Listo, compramos el Virtus! Lo retiramos el martes. Vendimos` → missing: ['VW Virtus 2024']
- **T41** `Lionel tiene una alergia alimentaria. Le dimos huevo por pri` → missing: ['Hospital Bouquet Roldán']
- **T44** `La Dra. Fernández nos dijo que avisemos en la guardería de l` → missing: ['Analía']
- **T48** `Para el cumple de 1 de Lionel estamos organizando una fiesta` → missing: ['Cumpleaños 1 año Lionel']
- **T49** `La torta la encargamos a Dulce María, una pastelería en el c` → missing: ['Dulce María']

## Relation Misses

- **T9** → missing: [['pequenos_pasos', 'cipolletti']]
- **T10** → missing: [['jardin_arcoiris', 'fernandez_oro']]
- **T12** → missing: [['dra_martinez', 'laura']]
- **T15** → missing: [['martin_sosa', 'rebalance'], ['rebalance', 'neuquen'], ['martin_sosa', 'laura']]
- **T16** → missing: [['libro_blw', 'blw']]
- **T24** → missing: [['rosa', 'general_roca']]
- **T25** → missing: [['valentina', 'diego']]
- **T26** → missing: [['cesat', 'cipolletti']]
- **T27** → missing: [['club_cipolletti', 'cipolletti']]
- **T29** → missing: [['osde', 'cipolletti']]
- **T30** → missing: [['sofia', 'pequenos_pasos']]
- **T34** → missing: [['marta', 'buenos_aires']]
- **T37** → missing: [['yacopini', 'neuquen']]
- **T42** → missing: [['dr_ruiz', 'ciarec'], ['ciarec', 'neuquen'], ['dr_ruiz', 'lionel']]
- **T44** → missing: [['analia', 'pequenos_pasos']]

## Fact Misses (training data candidates)

- **T4** `Fuimos al turno. Lionel pesó 8.2kg y midió 67cm. La doctora ` → missing: ['Peso: 8.2kg, talla: 67cm a los 6 meses', 'Resultado: peso y talla normales, vacunas aplicada']
- **T6** `La doctora nos dijo que ya podemos empezar con alimentación ` → missing: ['Inicia alimentación complementaria: zapallo, batat', 'Método elegido: BLW (Baby Led Weaning)']
- **T7** `Lionel está durmiendo horrible, se despierta cada 2 horas. L` → missing: ['Se despierta cada 2 horas de noche', 'Técnica recomendada: desvanecimiento gradual']
- **T10** `También vimos Jardín Arcoíris en Fernández Oro. Es más barat` → missing: ['Laura la prefiere por cercanía a su trabajo']
- **T11** `Decidimos ir con Pequeños Pasos. Arranca en agosto cuando Li` → missing: ['Lionel arranca en agosto con 8 meses', 'Requisitos: certificado de vacunas al día y apto m']
- **T13** `Tenemos OSDE 310, cubre bastante bien. Las consultas pediátr` → missing: ['Costo: 50.000 ARS por sesión, particular (no cubre']
- **T14** `¿Sabés si OSDE cubre kinesiólogo para Laura? Tiene dolor de ` → missing: ['Tiene dolor de espalda desde el embarazo, quiere i']
- **T15** `Laura empezó kinesiología con Martín Sosa en la clínica Reba` → missing: ['Kinesiología: 2 sesiones/semana, lunes y jueves. C']
- **T16** `Lionel probó zapallo hoy por primera vez. Le encantó. Mañana` → missing: ['Primera comida: zapallo, le gustó']
- **T17** `Me preocupa un poco que Lionel todavía no se sienta solo. La` → missing: ['Aún no se sienta solo, normal según pediatra hasta']
- **T18** `¿Podés anotar el calendario de vacunas que nos queda? A los ` → missing: ['Vacunas pendientes: 12m triple viral + hep A, 15-1']
- **T19** `Laura tuvo el control con la Dra. Martínez. Todo bien, le co` → missing: ['Resultado: todo bien, se colocó DIU Mirena, contro']
- **T20** `Lionel empezó a gatear!!! 🎉 tiene 7 meses y medio. Ahora hay` → missing: ['Empezó a gatear a los 7 meses y medio']
- **T21** `Lionel tiene fiebre, 38.5. Le dimos Ibueván gotas como nos d` → missing: ['Fiebre 38.5, medicado con Ibueván gotas', 'Si llega a 39 ir a guardia del Castro Rendón']
- **T22** `Bajó la fiebre a 37.2, parece que era por los dientes. Le es` → missing: ['Fiebre por dentición, le salen los dos incisivos i']
- **T29** `Anotá que tengo que renovar la credencial de OSDE de Lionel.` → missing: ['Pendiente: renovar credencial OSDE, llevar partida']
- **T30** `Lionel arrancó la guardería Pequeños Pasos hoy! Se quedó 2 h` → missing: ['Primer día de guardería: adaptación 2 horas, sin l']
- **T32** `Fuimos al control de los 9 meses. Lionel pesa 9.1kg, mide 72` → missing: ['Control 9 meses: peso 9.1kg, talla 72cm, vacuna an', 'Resultado: desarrollo conforme según pediatra']
- **T33** `La kinesióloga de Laura le dio el alta. Ya no tiene más dolo` → missing: ['Alta de kinesiología, ya sin dolor de espalda', 'Recomendación: ejercicio y fortalecer zona core']
- **T39** `Listo, compramos el Virtus! Lo retiramos el martes. Vendimos` → missing: ['Vendido en 12.000.000 ARS']
- **T41** `Lionel tiene una alergia alimentaria. Le dimos huevo por pri` → missing: ['Alergia alimentaria al huevo, reacción con ronchas']
- **T42** `La Dra. López nos derivó a un alergista. Sacamos turno con e` → missing: ['Derivado a alergista, pendiente análisis IgE espec']
- **T43** `Los resultados del alergista: Lionel tiene alergia al huevo ` → missing: ['Alergia al huevo confirmada (IgE positivo), alergi', 'Pronóstico: posible superación antes de los 3 años', 'Dieta: evitar huevo y derivados, leche en pequeñas']
- **T44** `La Dra. Fernández nos dijo que avisemos en la guardería de l` → missing: ['Tiene protocolo para alergias alimentarias']
- **T47** `Laura dice que vayamos con Sancor que tiene mejor reputación` → missing: ['Elegido como seguro de vida familiar, plan complet']

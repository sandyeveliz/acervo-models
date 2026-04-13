# Case Scenario: Fitness

**Turns:** 50 | **Passed:** 5/50 (10%)
**Entity acc:** 67% | **Relation acc:** 12% | **Fact acc:** 0% | **Topic acc:** 100%
**Graph:** 23 nodes, 39 edges | **Time:** 374.3s

## Turn-by-turn

| Turn | Ent% | Rel% | Fact% | Nodes | Δn | ms | Status |
|------|------|------|-------|-------|----|----|--------|
| 1 | 0% | — | — | 0 | +0 | 7702 | ✗ |
| 2 | 100% | 0% | — | 3 | +3 | 8703 | ✗ |
| 3 | — | — | 0% | 3 | +0 | 5938 | ✗ |
| 4 | — | — | 0% | 3 | +0 | 6405 | ✗ |
| 5 | 100% | — | 0% | 4 | +1 | 6780 | ✗ |
| 6 | 0% | 0% | — | 4 | +0 | 6030 | ✗ |
| 7 | — | — | 0% | 4 | +0 | 5594 | ✗ |
| 8 | 100% | — | — | 6 | +2 | 7219 | ✓ |
| 9 | — | — | 0% | 6 | +0 | 6421 | ✗ |
| 10 | — | — | 0% | 6 | +0 | 6297 | ✗ |
| 11 | 100% | 50% | — | 10 | +4 | 9000 | ✗ |
| 12 | — | — | 0% | 10 | +0 | 5686 | ✗ |
| 13 | — | — | 0% | 10 | +0 | 6734 | ✗ |
| 14 | — | — | 0% | 11 | +1 | 6936 | ✗ |
| 15 | — | — | 0% | 11 | +0 | 6891 | ✗ |
| 16 | 100% | — | — | 12 | +1 | 7014 | ✓ |
| 17 | — | — | 0% | 12 | +0 | 6453 | ✗ |
| 18 | — | — | 0% | 12 | +0 | 7563 | ✗ |
| 19 | — | — | 0% | 13 | +1 | 6983 | ✗ |
| 20 | — | — | 0% | 13 | +0 | 7125 | ✗ |
| 21 | — | — | 0% | 13 | +0 | 6860 | ✗ |
| 22 | — | — | 0% | 13 | +0 | 7280 | ✗ |
| 23 | — | — | 0% | 13 | +0 | 6344 | ✗ |
| 24 | — | — | 0% | 13 | +0 | 6250 | ✗ |
| 25 | 100% | — | — | 14 | +1 | 6780 | ✓ |
| 26 | — | — | 0% | 14 | +0 | 6640 | ✗ |
| 27 | — | — | 0% | 15 | +1 | 7936 | ✗ |
| 28 | — | — | — | 15 | +0 | 7266 | ✓ |
| 29 | 0% | — | — | 15 | +0 | 7030 | ✗ |
| 30 | — | — | 0% | 15 | +0 | 6890 | ✗ |
| 31 | — | — | 0% | 15 | +0 | 6717 | ✗ |
| 32 | — | — | 0% | 16 | +1 | 7907 | ✗ |
| 33 | 100% | — | 0% | 18 | +2 | 9061 | ✗ |
| 34 | 100% | 0% | — | 20 | +2 | 8719 | ✗ |
| 35 | — | — | 0% | 20 | +0 | 6375 | ✗ |
| 36 | — | — | 0% | 20 | +0 | 7078 | ✗ |
| 37 | — | — | 0% | 22 | +2 | 8233 | ✗ |
| 38 | — | — | 0% | 22 | +0 | 6782 | ✗ |
| 39 | — | — | 0% | 22 | +0 | 6671 | ✗ |
| 40 | — | — | 0% | 22 | +0 | 7907 | ✗ |
| 41 | — | — | 0% | 22 | +0 | 6327 | ✗ |
| 42 | — | — | 0% | 22 | +0 | 5890 | ✗ |
| 43 | — | — | 0% | 22 | +0 | 5984 | ✗ |
| 44 | 0% | — | — | 22 | +0 | 7297 | ✗ |
| 45 | — | — | 0% | 22 | +0 | 6500 | ✗ |
| 46 | — | — | 0% | 23 | +1 | 7405 | ✗ |
| 47 | — | — | 0% | 23 | +0 | 6358 | ✗ |
| 48 | — | — | 0% | 23 | +0 | 31782 | ✗ |
| 49 | — | — | 0% | 23 | +0 | 8546 | ✗ |
| 50 | — | — | — | 23 | +0 | 5969 | ✓ |

## Entity Misses (training data candidates)

- **T1** `Quiero empezar a entrenar en serio. Hoy peso 92kg, mido 1.78` → missing: ['Sandy']
- **T6** `Fui al nutricionista Ezequiel Flores. Tiene consultorio en C` → missing: ['Ezequiel Flores']
- **T29** `Ok, me anoto! Media maratón de Neuquén en 4 meses. Objetivo:` → missing: ['Media Maratón Neuquén']
- **T44** `Gustavo me convenció de anotarnos en una maratón completa en` → missing: ['Maratón Buenos Aires']

## Relation Misses

- **T2** → missing: [['marcos', 'crossfit_plottier']]
- **T6** → missing: [['ezequiel_flores', 'cipolletti']]
- **T11** → missing: [['medisur', 'neuquen']]
- **T34** → missing: [['locos_x_correr', 'neuquen']]

## Fact Misses (training data candidates)

- **T3** `Marcos me armó una rutina de 3 bloques: calentamiento 10min,` → missing: ['Rutina: calentamiento 10min + WOD 25min + enfriami']
- **T4** `Hoy hice mi primer benchmark WOD: Fran. Son 21-15-9 de thrus` → missing: ['Benchmark Fran: 8:45 (21-15-9 thrusters + pull-ups']
- **T5** `Para las corridas, estoy usando la app Strava para trackear.` → missing: ['Corrida 5km: mejor tiempo 28:30, objetivo sub-25']
- **T7** `El plan de Ezequiel: 2200 calorías diarias, 160g proteína, 2` → missing: ['Plan nutricional: 2200 cal, 160g prot, 200g carb, ']
- **T9** `Después de 2 semanas: peso 91.2kg, bajé 800g. No es mucho pe` → missing: ['Semana 2: 91.2kg (-800g). Más energía']
- **T10** `Hoy me lesioné el hombro derecho haciendo overhead press. No` → missing: ['Lesión hombro derecho en overhead press. Descanso ']
- **T12** `Mientras me recupero del hombro, Marcos me arma rutinas de p` → missing: ['Rutina modificada: solo piernas y core por lesión ']
- **T13** `Hoy corrí 5km en 27:15! Mejoré más de un minuto. Creo que el` → missing: ['Record 5km: 27:15 (mejora de 1:15 vs anterior)']
- **T14** `El hombro ya está mejor, el Dr. Navarro me dio el alta de ki` → missing: ['Alta de kine hombro, volver a tren superior con pe']
- **T15** `Mes 1 completo: peso 90.4kg (-1.6kg). Las medidas: cintura 9` → missing: ['Mes 1: 90.4kg (-1.6). Cintura 94cm (-4), pecho 104']
- **T17** `Marcos me armó un plan de running para la carrera: 3 corrida` → missing: ['Plan: mar tempo 5km, jue 8km lento, sáb long run p']
- **T18** `Laura quiere empezar a entrenar también. Le recomendé CrossF` → missing: ['Quiere empezar CrossFit, horario 9am']
- **T19** `Laura arrancó CrossFit! Le encantó. Marcos le armó una rutin` → missing: ['Inició CrossFit Plottier, clase 9am lunes y miérco']
- **T20** `Compré una cuerda para saltar y un par de mancuernas de 10kg` → missing: ['Equipamiento casa: cuerda para saltar + mancuernas']
- **T21** `Long run de hoy: 12km en 1:08. Me sentí bien hasta el km 10,` → missing: ['Long run 12km en 1:08. Flaqueó km 10, mejorar hidr']
- **T22** `Ezequiel ajustó la dieta: sumó 200 calorías los días de corr` → missing: ['Dieta ajustada: +200cal días long run, carbo loadi']
- **T23** `Mes 2: peso 88.7kg (-3.3kg total). Ya se nota la diferencia ` → missing: ['Mes 2: 88.7kg (-3.3 total). Cintura 91cm (-7)']
- **T24** `Hice Fran otra vez para comparar. Esta vez 7:20, ¡mejoré 1:2` → missing: ['Benchmark Fran actualizado: 7:20 (mejora 1:25 vs 8']
- **T26** `La Corrida del Río es este fin de semana! Estoy nervioso per` → missing: ['Carrera este fin de semana']
- **T27** `TERMINÉ LA CARRERA!! 10km en 52:38!!! Superé mi objetivo de ` → missing: ['Resultado: 52:38, objetivo sub-55 cumplido', 'Resultado Corrida del Río: 48 minutos']
- **T30** `Marcos dice que para la media necesito subir a 4 corridas se` → missing: ['Plan media maratón: 4 corridas/sem, CrossFit baja ']
- **T31** `Mes 3: peso 87.5kg (-4.5kg total). A 2.5kg del objetivo de 8` → missing: ['Mes 3: 87.5kg (-4.5 total). Cintura 88cm. A 2.5kg ']
- **T32** `Hoy hice mi primer long run de 16km. Tardé 1:33. Las piernas` → missing: ['Long run 16km en 1:33. Sin parar. Sales de hidrata']
- **T33** `Gustavo y yo corrimos juntos el sábado. Me enseñó el tema de` → missing: ['Aprendiendo zonas cardíacas, entrenar en zona 2 lo']
- **T35** `Marcos me agregó ejercicios de fortalecimiento de core y glú` → missing: ['Prevención lesiones: planchas, hip thrust, step up']
- **T36** `Long run de 18km! Mi más largo ever. 1:46. Me sentí fuerte h` → missing: ['Long run 18km en 1:46, se sintió fuerte']
- **T37** `Ezequiel me dijo que cargue carbohidratos 3 días antes de la` → missing: ['Carbo loading 3 días antes. Carrera: banana + mant']
- **T38** `Mes 4: peso 85.8kg! Casi en el objetivo de 85! Nunca me sent` → missing: ['Mes 4: 85.8kg (-6.2 total). Casi en objetivo de 85']
- **T39** `La media maratón es este domingo! Plan: salir conservador lo` → missing: ['Estrategia: conservador 0-10km, ritmo 10-18km, spr']
- **T40** `MEDIA MARATÓN COMPLETADA!!! 21km en 1:58:42. Bajé de las 2 h` → missing: ['Resultado: 1:58:42 (sub-2h!!)', 'Resultado media maratón: 1:45']
- **T41** `Después de la media me tomé una semana de descanso total. So` → missing: ['Semana descanso post media maratón']
- **T42** `Objetivo cumplido: hoy me pesé y estoy en 85.1kg!! Prácticam` → missing: ['OBJETIVO CUMPLIDO: 85.1kg (de 92kg en 4.5 meses, -']
- **T43** `Marcos dice que ahora el objetivo debería ser mantener y gan` → missing: ['Nueva fase: mantenimiento + hipertrofia. Subir cal']
- **T45** `Laura ya baja 3kg desde que empezó CrossFit. Está re motivad` → missing: ['Bajó 3kg con CrossFit, quiere empezar running']
- **T46** `Me compré un foam roller y una pistola de masaje para recupe` → missing: ['Equipamiento recuperación: foam roller 25K + pisto']
- **T47** `Nuevo PR en Fran: 6:15!! De 8:45 a 6:15 en 4 meses. Marcos d` → missing: ['Benchmark Fran PR: 6:15 (de 8:45, mejora 2:30 en 4']
- **T48** `5km PR: 24:32!!! Bajé de 25 minutos que era mi objetivo orig` → missing: ['5km PR: 24:32 (de 28:30, mejora 3:58)']
- **T49** `Resumen de todo el proceso: 92→85kg, 5km de 28:30→24:32, Fra` → missing: ['Resumen 4.5 meses: 92→85kg, 5km 28:30→24:32, Fran ']

# Case Scenario: Libro

**Turns:** 50 | **Passed:** 6/50 (12%)
**Entity acc:** 70% | **Relation acc:** 3% | **Fact acc:** 8% | **Topic acc:** 94%
**Graph:** 57 nodes, 130 edges | **Time:** 413.6s

## Turn-by-turn

| Turn | Ent% | Rel% | Fact% | Nodes | Δn | ms | Status |
|------|------|------|-------|-------|----|----|--------|
| 1 | 100% | 0% | — | 2 | +2 | 7640 | ✗ |
| 2 | 100% | 0% | — | 5 | +3 | 7813 | ✗ |
| 3 | 100% | 0% | 0% | 6 | +1 | 7608 | ✗ |
| 4 | — | — | 0% | 6 | +0 | 5641 | ✗ |
| 5 | 0% | 0% | 0% | 7 | +1 | 6577 | ✗ |
| 6 | 0% | 33% | — | 9 | +2 | 10655 | ✗ |
| 7 | 100% | 0% | 0% | 11 | +2 | 10203 | ✗ |
| 8 | 100% | 0% | 0% | 12 | +1 | 7703 | ✗ |
| 9 | 100% | 0% | 0% | 13 | +1 | 7171 | ✗ |
| 10 | 0% | — | 0% | 13 | +0 | 6953 | ✗ |
| 11 | 100% | 0% | 0% | 16 | +3 | 10578 | ✗ |
| 12 | 100% | — | 0% | 17 | +1 | 8733 | ✗ |
| 13 | — | — | 0% | 18 | +1 | 7844 | ✗ |
| 14 | — | — | 0% | 19 | +1 | 7750 | ✗ |
| 15 | 100% | — | 100% | 21 | +2 | 8547 | ✓ |
| 16 | 100% | 0% | 0% | 22 | +1 | 7936 | ✗ |
| 17 | 100% | 0% | 0% | 24 | +2 | 9030 | ✗ |
| 18 | — | — | 0% | 24 | +0 | 7578 | ✗ |
| 19 | 0% | — | 0% | 24 | +0 | 7342 | ✗ |
| 20 | — | — | 0% | 24 | +0 | 6532 | ✗ |
| 21 | — | — | — | 24 | +0 | 6061 | ✓ |
| 22 | 100% | 0% | — | 26 | +2 | 7188 | ✗ |
| 23 | — | — | 100% | 27 | +1 | 8859 | ✓ |
| 24 | 67% | 0% | — | 30 | +3 | 8483 | ✗ |
| 25 | — | — | 0% | 30 | +0 | 6453 | ✗ |
| 26 | — | — | 0% | 30 | +0 | 7296 | ✗ |
| 27 | — | — | 0% | 30 | +0 | 9250 | ✗ |
| 28 | — | — | 0% | 31 | +1 | 8250 | ✗ |
| 29 | 100% | 0% | 100% | 33 | +2 | 9235 | ✗ |
| 30 | — | — | 0% | 39 | +6 | 15467 | ✗ |
| 31 | — | — | — | 40 | +1 | 6984 | ✓ |
| 32 | 50% | 0% | — | 41 | +1 | 7186 | ✗ |
| 33 | 100% | 50% | 0% | 43 | +2 | 9313 | ✗ |
| 34 | — | — | 0% | 43 | +0 | 9703 | ✗ |
| 35 | — | — | 0% | 44 | +1 | 6811 | ✗ |
| 36 | 0% | — | 0% | 44 | +0 | 14265 | ✗ |
| 37 | — | — | 0% | 44 | +0 | 7672 | ✗ |
| 38 | 100% | 0% | 0% | 44 | +0 | 7702 | ✗ |
| 39 | — | — | — | 45 | +1 | 8563 | ✓ |
| 40 | 0% | 0% | — | 45 | +0 | 7250 | ✗ |
| 41 | 100% | 0% | 0% | 46 | +1 | 8703 | ✗ |
| 42 | 0% | 0% | 0% | 47 | +1 | 7733 | ✗ |
| 43 | 100% | 0% | 0% | 50 | +3 | 8344 | ✗ |
| 44 | 100% | 0% | 0% | 52 | +2 | 8484 | ✗ |
| 45 | 100% | 0% | 0% | 53 | +1 | 7000 | ✗ |
| 46 | — | — | 0% | 53 | +0 | 7311 | ✗ |
| 47 | — | — | 0% | 56 | +3 | 9125 | ✗ |
| 48 | 0% | 0% | 0% | 56 | +0 | 7688 | ✗ |
| 49 | — | — | 0% | 57 | +1 | 9109 | ✗ |
| 50 | — | — | — | 57 | +0 | 8313 | ✓ |

## Entity Misses (training data candidates)

- **T5** `El realismo mágico es fundamental. Lo sobrenatural se presen` → missing: ['Remedios la Bella']
- **T6** `Hagamos un mapa de la familia Buendía. Primera generación: J` → missing: ['José Arcadio (hijo)', 'Amaranta Buendía']
- **T10** `¿Cuál es tu interpretación de por qué el pueblo se llama Mac` → missing: ['Aracataca']
- **T19** `El último Aureliano descifra los pergaminos de Melquíades al` → missing: ['Último Aureliano']
- **T24** `Los personajes principales son Horacio Oliveira, un intelect` → missing: ['La Maga (Lucía)']
- **T32** `Ahora quiero arrancar con 'El túnel' de Ernesto Sábato. Es m` → missing: ['Ernesto Sábato']
- **T36** `Los celos de Castel son enfermizos. Sospecha de todos: de Al` → missing: ['Allende', 'Hunter']
- **T40** `Voy a leer Ficciones de Borges. Lo tengo hace años en la bib` → missing: ['Ficciones', 'Jorge Luis Borges']
- **T42** `'El jardín de senderos que se bifurcan' es impresionante. Es` → missing: ['El jardín de senderos que se bifurcan']
- **T48** `'Funes el memorioso' lo leí anoche. Un tipo que después de u` → missing: ['Funes el memorioso']

## Relation Misses

- **T1** → missing: [['cien_anos', 'garcia_marquez']]
- **T2** → missing: [['jose_arcadio_buendia', 'macondo'], ['jose_arcadio_buendia', 'cien_anos'], ['ursula', 'cien_anos']]
- **T3** → missing: [['coronel_aureliano', 'cien_anos']]
- **T5** → missing: [['remedios_bella', 'cien_anos']]
- **T6** → missing: [['jose_arcadio_hijo', 'jose_arcadio_buendia'], ['coronel_aureliano', 'jose_arcadio_buendia']]
- **T7** → missing: [['rebeca', 'jose_arcadio_hijo'], ['remedios_moscote', 'coronel_aureliano']]
- **T8** → missing: [['melquiades', 'cien_anos']]
- **T9** → missing: [['casa_buendia', 'macondo']]
- **T11** → missing: [['masacre_bananeras', 'cien_anos'], ['jose_arcadio_segundo', 'masacre_bananeras']]
- **T16** → missing: [['fernanda', 'aureliano_segundo']]
- **T17** → missing: [['meme', 'aureliano_segundo']]
- **T22** → missing: [['rayuela', 'cortazar']]
- **T24** → missing: [['oliveira', 'rayuela'], ['la_maga', 'rayuela'], ['oliveira', 'club_serpiente'], ['la_maga', 'club_serpiente']]
- **T29** → missing: [['traveler', 'rayuela'], ['talita', 'rayuela']]
- **T32** → missing: [['el_tunel', 'sabato']]
- **T33** → missing: [['castel', 'el_tunel']]
- **T38** → missing: [['garcia_marquez', 'boom_latinoamericano'], ['cortazar', 'boom_latinoamericano'], ['sabato', 'boom_latinoamericano']]
- **T40** → missing: [['ficciones', 'borges'], ['borges', 'boom_latinoamericano']]
- **T41** → missing: [['tlon', 'ficciones']]
- **T42** → missing: [['jardin_senderos', 'ficciones']]
- **T43** → missing: [['biblioteca_babel', 'ficciones']]
- **T44** → missing: [['pierre_menard', 'ficciones']]
- **T45** → missing: [['loteria_babilonia', 'ficciones']]
- **T48** → missing: [['funes', 'ficciones']]

## Fact Misses (training data candidates)

- **T3** `Uno de los temas centrales es la soledad. Cada personaje exp` → missing: ['Tema central: la soledad, cada personaje la experi', 'Se aísla en laboratorio de alquimia', 'Se endurece tras 32 guerras civiles perdidas']
- **T4** `Otro tema es la circularidad del tiempo. Los nombres se repi` → missing: ['Tema: circularidad del tiempo. Nombres y destinos ']
- **T5** `El realismo mágico es fundamental. Lo sobrenatural se presen` → missing: ['Realismo mágico: lo sobrenatural como cotidiano. L']
- **T7** `Segunda generación: José Arcadio (hijo) se casa con Rebeca. ` → missing: ['Nunca se casa, rechaza todos los pretendientes']
- **T8** `Melquíades es un personaje clave. Es un gitano que visita Ma` → missing: ['Trae inventos a Macondo: imán, lupa, hielo. Escrib']
- **T9** `La casa de los Buendía es casi un personaje más. Empieza com` → missing: ['Evolución: de barro y caña → mansión → ruinas inva']
- **T10** `¿Cuál es tu interpretación de por qué el pueblo se llama Mac` → missing: ['Nombre posiblemente tomado de finca bananera cerca']
- **T11** `Hablemos de la masacre de las bananeras. Es uno de los momen` → missing: ['Basada en la masacre real de United Fruit Company ']
- **T12** `Los gemelos José Arcadio Segundo y Aureliano Segundo son de ` → missing: ['Introvertido, obsesionado con los pergaminos de Me', 'Extrovertido, derrochador. Opuesto a su gemelo']
- **T13** `El diluvio de cuatro años es otro evento mágico brutal. Llue` → missing: ['El diluvio: 4 años, 11 meses, 2 días de lluvia con']
- **T14** `Analicemos los personajes femeninos. Úrsula es el pilar de l` → missing: ['Pilar de la familia, vive 100+ años. Su muerte mar']
- **T16** `Fernanda del Carpio es interesante. Viene de una familia ari` → missing: ['Aristocrática, rígida, religiosa. Choca con la cul']
- **T17** `Meme (Renata Remedios) es hija de Aureliano Segundo y Fernan` → missing: ['Enviada al convento por Fernanda por su relación c', 'Caracterizado por mariposas amarillas que lo rodea']
- **T18** `Las mariposas amarillas de Mauricio Babilonia son uno de los` → missing: ['Mariposas amarillas desaparecen cuando lo hieren d']
- **T19** `El último Aureliano descifra los pergaminos de Melquíades al` → missing: ['Final: último Aureliano descifra pergaminos mientr', 'Pergaminos escritos en sánscrito, contenían toda l']
- **T20** `La frase final del libro es devastadora. Algo como que las e` → missing: ['Final circular: el fin estaba predestinado desde e']
- **T25** `El libro se divide en: 'Del lado de allá' (París), 'Del lado` → missing: ['3 partes: Del lado de allá (París), Del lado de ac']
- **T26** `Oliveira es un personaje difícil. Es super intelectual pero ` → missing: ['Intelectual pero emocionalmente incapaz. Pierde a ']
- **T27** `La Maga es lo opuesto a Oliveira: intuitiva, emocional, vive` → missing: ['Intuitiva, emocional, opuesta a Oliveira. Él la ad']
- **T28** `El capítulo 7 es el más famoso. Es el del beso bajo la lluvi` → missing: ['Capítulo 7: escena del beso bajo la lluvia, consid']
- **T30** `El tema del jazz es importante en Rayuela. El Club de la Ser` → missing: ['Jazz como tema central: Parker, Monk, Bessie Smith']
- **T33** `El túnel arranca con Juan Pablo Castel diciendo que mató a M` → missing: ['Estructura: confesión del asesinato de María por C']
- **T34** `Castel es un pintor reconocido pero profundamente aislado. S` → missing: ['Pintor reconocido pero aislado. Se obsesiona con M', 'Cuadro clave: ventanita con mujer solitaria en la ']
- **T35** `El túnel del título es la metáfora de la soledad de Castel. ` → missing: ['Metáfora del túnel: soledad como túneles paralelos']
- **T36** `Los celos de Castel son enfermizos. Sospecha de todos: de Al` → missing: ['Celos patológicos: sospecha de Allende (esposo cie']
- **T37** `Es interesante comparar la soledad en El túnel vs Cien años ` → missing: ['Soledad individual, psicológica, claustrofóbica (v']
- **T38** `Los tres libros que leí (Cien años, Rayuela, El túnel) son d` → missing: ['Estilos contrastados: Márquez (barroco/mágico), Co']
- **T41** `Empecé con 'Tlön, Uqbar, Orbis Tertius'. Es una locura. Es s` → missing: ['Enciclopedia de mundo ficticio Tlön donde el ideal']
- **T42** `'El jardín de senderos que se bifurcan' es impresionante. Es` → missing: ['Cuento de espionaje que reflexiona sobre tiempo y ']
- **T43** `'La biblioteca de Babel' me hizo pensar en Acervo! Una bibli` → missing: ['Biblioteca infinita con todos los libros posibles.']
- **T44** `'Pierre Menard, autor del Quijote' es genial y absurdo. Un e` → missing: ['Tema: mismo texto, distinto contexto = distinto si']
- **T45** `'La lotería en Babilonia' describe una sociedad donde todo s` → missing: ['Sociedad donde todo se decide por sorteo. Metáfora']
- **T46** `Borges es completamente distinto a los otros tres. No escrib` → missing: ['Estilo: cuentos cortos, ideas sobre emociones, ens']
- **T47** `Me falta leer 'Las ruinas circulares', 'Funes el memorioso',` → missing: ['Pendientes: Las ruinas circulares, Funes el memori']
- **T48** `'Funes el memorioso' lo leí anoche. Un tipo que después de u` → missing: ['Memoria perfecta paraliza el pensamiento. Pensar r']
- **T49** `Funes me hace pensar de nuevo en Acervo. Un sistema de memor` → missing: ['Analogía Acervo: memoria perfecta sin compresión =']

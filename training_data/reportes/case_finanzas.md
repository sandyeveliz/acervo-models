# Case Scenario: Finanzas

**Turns:** 49 | **Passed:** 13/49 (27%)
**Entity acc:** 40% | **Relation acc:** 0% | **Fact acc:** 0% | **Topic acc:** 100%
**Graph:** 23 nodes, 30 edges | **Time:** 326.2s

## Turn-by-turn

| Turn | Ent% | Rel% | Fact% | Nodes | Δn | ms | Status |
|------|------|------|-------|-------|----|----|--------|
| 1 | — | — | 0% | 0 | +0 | 6625 | ✗ |
| 2 | — | — | 0% | 0 | +0 | 6561 | ✗ |
| 3 | — | — | 0% | 0 | +0 | 5530 | ✗ |
| 4 | 0% | — | — | 0 | +0 | 5484 | ✗ |
| 5 | — | — | — | 0 | +0 | 5422 | ✓ |
| 6 | — | — | — | 0 | +0 | 5483 | ✓ |
| 7 | 100% | — | — | 3 | +3 | 7266 | ✓ |
| 8 | — | — | 0% | 4 | +1 | 7421 | ✗ |
| 9 | — | — | 0% | 4 | +0 | 5796 | ✗ |
| 10 | 0% | 0% | — | 4 | +0 | 5907 | ✗ |
| 11 | 0% | — | — | 4 | +0 | 5327 | ✗ |
| 12 | — | — | 0% | 4 | +0 | 6390 | ✗ |
| 13 | 0% | — | — | 7 | +3 | 8016 | ✗ |
| 14 | 0% | 0% | — | 7 | +0 | 7796 | ✗ |
| 15 | 100% | — | 0% | 8 | +1 | 6436 | ✗ |
| 16 | 100% | — | — | 10 | +2 | 6609 | ✓ |
| 17 | 100% | — | 0% | 11 | +1 | 8078 | ✗ |
| 18 | — | — | — | 11 | +0 | 5842 | ✓ |
| 19 | — | — | 0% | 11 | +0 | 6078 | ✗ |
| 20 | — | — | 0% | 11 | +0 | 7188 | ✗ |
| 21 | — | — | 0% | 11 | +0 | 6530 | ✗ |
| 22 | — | — | 0% | 12 | +1 | 7015 | ✗ |
| 23 | — | — | 0% | 13 | +1 | 7250 | ✗ |
| 24 | — | — | 0% | 13 | +0 | 6186 | ✗ |
| 25 | 0% | — | — | 13 | +0 | 5844 | ✗ |
| 26 | — | 0% | 0% | 13 | +0 | 6703 | ✗ |
| 27 | — | — | 0% | 13 | +0 | 7827 | ✗ |
| 28 | — | — | 0% | 13 | +0 | 7235 | ✗ |
| 29 | — | — | 0% | 13 | +0 | 6375 | ✗ |
| 30 | — | — | 0% | 13 | +0 | 6780 | ✗ |
| 31 | 0% | — | 0% | 13 | +0 | 6594 | ✗ |
| 32 | — | — | — | 13 | +0 | 5827 | ✓ |
| 33 | — | — | 0% | 13 | +0 | 6453 | ✗ |
| 34 | — | — | 0% | 13 | +0 | 6219 | ✗ |
| 35 | 0% | — | 0% | 14 | +1 | 8375 | ✗ |
| 36 | — | — | 0% | 14 | +0 | 6452 | ✗ |
| 37 | — | — | — | 14 | +0 | 5875 | ✓ |
| 38 | 0% | 0% | 0% | 15 | +1 | 7328 | ✗ |
| 39 | — | — | — | 15 | +0 | 5875 | ✓ |
| 40 | — | — | 0% | 15 | +0 | 7046 | ✗ |
| 41 | — | — | — | 16 | +1 | 6375 | ✓ |
| 42 | — | — | 0% | 16 | +0 | 6703 | ✗ |
| 43 | — | — | 0% | 17 | +1 | 7546 | ✗ |
| 44 | — | — | 0% | 20 | +3 | 9922 | ✗ |
| 45 | 100% | — | — | 22 | +2 | 6967 | ✓ |
| 46 | — | — | — | 22 | +0 | 5921 | ✓ |
| 47 | — | — | 0% | 22 | +0 | 6969 | ✗ |
| 48 | 100% | — | — | 23 | +1 | 6703 | ✓ |
| 49 | — | — | — | 23 | +0 | 6094 | ✓ |

## Entity Misses (training data candidates)

- **T4** `Mis metas de ahorro son 5: fondo de emergencia (6 meses de g` → missing: ['Fondo de Emergencia', 'Fondo Viaje 2027', 'Fondo Universidad Lionel', 'Fondo Jubilación', 'Fondo Casa Propia']
- **T10** `Ok, puse 1.000.000 ARS en el FCI Balanz Ahorro en pesos (mon` → missing: ['Balanz Ahorro']
- **T11** `Para el viaje necesito dólares. ¿Cómo compro dólar MEP? Vi q` → missing: ['Dólar MEP', 'AL30']
- **T13** `Para el largo plazo quiero meter algo en CEDEARs. Me interes` → missing: ['CEDEARs']
- **T14** `Compré mis primeros CEDEARs: 5 de Apple (AAPL) a 18.500 ARS ` → missing: ['AAPL (CEDEAR)', 'MELI (CEDEAR)']
- **T25** `Estoy viendo bonos CER para protegerme de la inflación. El T` → missing: ['TX26', 'TX28']
- **T31** `Gastos extra este mes: arreglo del lavarropas 80.000, cumple` → missing: ['Rocco']
- **T35** `Con el aumento, quiero meter 300.000 más por mes en CEDEARs.` → missing: ['GOOGL (CEDEAR)', 'AMZN (CEDEAR)']
- **T38** `Decidí hacer un split: 60% del fondo de emergencia en money ` → missing: ['Balanz Renta Fija']

## Relation Misses

- **T10** → missing: [['balanz_ahorro', 'fondo_emergencia']]
- **T14** → missing: [['apple_cedear', 'fondo_jubilacion'], ['meli_cedear', 'fondo_jubilacion']]
- **T26** → missing: [['tx28', 'fondo_casa']]
- **T38** → missing: [['balanz_renta_fija', 'fondo_emergencia']]

## Fact Misses (training data candidates)

- **T1** `Quiero empezar a organizar mis finanzas. Mi sueldo hoy son 4` → missing: ['Sueldo: 4.000.000 ARS/mes, monotributista categorí']
- **T2** `Los gastos fijos mensuales son: alquiler 350.000 ARS, OSDE 2` → missing: ['Gastos fijos mensuales: alquiler 350K, OSDE 280K, ']
- **T3** `O sea que me quedan como 2.500.000 ARS libres por mes. De es` → missing: ['Capacidad de ahorro: ~2.500.000 ARS/mes']
- **T8** `Abrí cuenta en Balanz. Ya hice la verificación de identidad ` → missing: ['Cuenta abierta y verificada, primera transferencia']
- **T9** `Para el fondo de emergencia, ¿me conviene un FCI money marke` → missing: ['Plazo fijo: 75% TNA']
- **T12** `Hice mi primera operación de dólar MEP. Compré AL30 en pesos` → missing: ['Primera compra: 450 USD via MEP a 1.111 ARS/USD']
- **T15** `El contador Pablo Méndez me dijo que los CEDEARs pagan impue` → missing: ['Pagan impuesto a las ganancias, declarar en DJ anu', 'FCI money market exento de ganancias']
- **T17** `Abrí cuenta en Ripio. Compré 0.005 BTC y 0.05 ETH con 200.00` → missing: ['Compra: 0.005 BTC por 200K ARS (parte)', 'Compra: 0.05 ETH por 200K ARS (parte)']
- **T19** `Me gustaría hacer un rebalanceo mensual. El día 5 de cada me` → missing: ['Plan de distribución mensual (día 5): 40% emergenc']
- **T20** `Anotá que las cuotas del préstamo del Virtus son 520.000 ARS` → missing: ['Préstamo auto Virtus: 520.000 ARS/mes, débito el 1']
- **T21** `Hoy cobré y distribuí como acordamos: 1.000.000 al money mar` → missing: ['Distribución abril: 1M money market, 500K MEP, 500']
- **T22** `MELI subió un 15% desde que compré!! Ahora cada CEDEAR vale ` → missing: ['Subió 15%, valor actual: 109.250 ARS c/u (compra f']
- **T23** `El dólar MEP subió a 1.180 ARS. Ahora tengo 450 USD + compré` → missing: ['Progreso: 870 USD de 5.000 USD (17.4%). Dólar MEP ']
- **T24** `Pablo Méndez me dijo que puedo deducir el alquiler de gananc` → missing: ['Puede deducir alquiler de ganancias con factura, a']
- **T26** `Compré 500.000 nominales de TX28 a 1.850 ARS cada 100 nomina` → missing: ['Compra: 500K nominales a 1.850 ARS/100VN']
- **T27** `Laura quiere que abramos una caja de ahorro en dólares en el` → missing: ['Plan: abrir caja de ahorro USD en Banco Patagonia ']
- **T28** `Abrimos la caja de ahorro en USD. Transferí los 870 USD de B` → missing: ['Caja de ahorro USD abierta, 870 USD transferidos d', 'Ahorro en caja de ahorro USD del Banco Patagonia']
- **T29** `Mi hermano Diego me preguntó si puede invertir conmigo en al` → missing: ['Quiere invertir 500K ARS a 3 meses en algo seguro']
- **T30** `Update del portafolio a fin de mes: money market 2.100.000 A` → missing: ['Portfolio fin de mes: MM 2.1M ARS, viaje 1.290 USD']
- **T31** `Gastos extra este mes: arreglo del lavarropas 80.000, cumple` → missing: ['Gastos imprevistos del mes: lavarropas 80K, regalo']
- **T33** `El alquiler sube en julio a 420.000 ARS, ajuste semestral de` → missing: ['Alquiler sube a 420.000 ARS en julio (ajuste semes']
- **T34** `Buenas noticias: me aumentaron el sueldo a 4.800.000 ARS a p` → missing: ['Aumento sueldo a 4.800.000 ARS desde agosto']
- **T35** `Con el aumento, quiero meter 300.000 más por mes en CEDEARs.` → missing: ['Plan: 300K ARS/mes adicionales en CEDEARs desde ag']
- **T36** `El fondo de emergencia ya tiene 4.200.000 ARS! Nos falta la ` → missing: ['Progreso: 4.200.000 ARS de 8.640.000 (48.6%), ~4 m']
- **T38** `Decidí hacer un split: 60% del fondo de emergencia en money ` → missing: ['Distribución: 60% money market (inmediata) + 40% r']
- **T40** `El Bitcoin pegó un salto, mi 0.01 BTC ahora vale 180.000 ARS` → missing: ['0.01 BTC pasó de 100K a 180K ARS (+80%)', 'ETH subió 25% desde compra']
- **T42** `Compromiso con Laura: bajo cripto del 10% al 5% y subo casa ` → missing: ['Nueva distribución mensual: 40% emergencia, 20% vi']
- **T43** `Me llegó un bono de fin de año de un cliente: 2.000.000 ARS ` → missing: ['Bono cliente 2M ARS → todo a dólar MEP, total esti']
- **T44** `Resumen del año: arranqué con 0 en inversiones, hoy tengo ~8` → missing: ['Portfolio a 8 meses: ~8M ARS (MM+RF), 2.500 USD (v']
- **T47** `Ah, me olvidé de contarte que cancelé anticipadamente 5 cuot` → missing: ['Préstamo auto: cancelación anticipada 5 cuotas (2.']

# BOM del prototipo V1

Precios estimados en USD, sin envío ni impuestos.

## Nivel A — validar el video (~$125)

Objetivo: transmitir 720p30 por WiFi y por LTE antes de invertir en la etapa de potencia.

| Pieza | Modelo sugerido | Cant | USD |
|---|---|---|---|
| Raspberry Pi Zero 2 W | SC0510, sin header | 1 | 15 |
| Cámara | Camera Module 3 o Zero Cam | 1 | 25 |
| Cable FFC CSI | 15 pines, 1.0 mm, 50 cm | 1 | 4 |
| microSD | 32 GB, clase A2 | 1 | 9 |
| Alimentación | power bank 5 V / 3 A | 1 | 20 |
| Módem LTE | Quectel EC25-E mini-PCIe | 1 | 32 |
| Adaptador | USB ↔ mini-PCIe | 1 | 12 |
| Cable y conectores | FFC hembra, dupont | 1 | 8 |
| **Subtotal** | | | **125** |

## Nivel B — prototipo completo (+$67)

| Pieza | Modelo sugerido | Cant | USD |
|---|---|---|---|
| Batería | LiPo 1S 4000 mAh, 52×56×10 mm | 1 | 14 |
| Cargador | BQ25895 breakout | 1 | 15 |
| Boost 5 V | TPS61088 o MT3608 | 1 | 6 |
| Fuel gauge | MAX17048 | 1 | 8 |
| Hub USB | SL2.1A | 1 | 4 |
| Micrófonos | INMP441 I²S | 2 | 6 |
| Audio | MAX98357A + altavoz 1 W | 1 | 8 |
| LED + resistencia | 3 mm rojo | 1 | 1 |
| Filamento | PETG 1 kg | 1 | 5 |
| **Subtotal** | | | **67** |

**Total A + B: $192**

## Criterios de aceptación

| Prueba | Objetivo |
|---|---|
| Video | 720p30 durante 10 min sin frames caídos |
| CPU de la Pi | < 70 % durante el stream |
| Latencia de video | < 6 s de cámara a plataforma |
| Voz con el agente | < 3 s ida y vuelta |
| Autonomía | > 4 h con 4000 mAh |
| Temperatura | < 45 °C en la carcasa al contacto |

## Orden de armado

1. Pi + cámara + cable en la mesa: directo privado y medición de CPU.
2. Power bank: medir consumo real contra los 2.5 W simulados.
3. EC25: repetir el directo por LTE y medir subida.
4. Audio: micrófonos, altavoz y lazo de voz.
5. Etapa de potencia propia: medir autonomía.
6. Carcasa: imprimir con las medidas reales del ensamble, no con las teóricas.

No imprimir nada antes del paso 5.

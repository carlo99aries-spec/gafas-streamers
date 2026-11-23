# Arquitectura

## Módulos

### Módulo A — lentes (cabeza de sensores)

| Elemento | Función |
|---|---|
| Cámara CSI | video para el directo y visión para el agente |
| 2 micrófonos I2S | captura con beamforming y cancelación de viento |
| Altavoz + amplificador | respuesta del agente al oído |
| LED de grabación | indicador visible de que se está grabando |

Peso objetivo: **~35 g**. Sin batería, sin radio, sin cómputo.
Toda la energía y los datos viajan por el cable.

### Módulo B — unidad (cuerpo)

| Elemento | Función |
|---|---|
| Raspberry Pi Zero 2 W | codificación H.264 por hardware, RTMP, puente de voz |
| Módem Quectel EC25 | LTE Cat 4 |
| Batería LiPo 4000 mAh | 4.9 h de operación |
| BQ25895 | carga con *power path* |
| TPS61088 | boost 3.7 → 5 V @ 2.5 A |
| MAX17048 | fuel gauge por I²C |
| Hub SL2.1A | módem + puerto de servicio (la Pi tiene un solo USB OTG) |

Dimensiones: **78 × 64 × 22 mm**. Peso objetivo: **~150 g**.

## Cadena de energía

```
USB-C ──▶ BQ25895 ──┬──▶ SYS ──▶ TPS61088 ──▶ 5 V ──▶ Pi Zero 2 W
                    │
                    └──▶ VBAT ──▶ LiPo 4000 mAh ──▶ MAX17048 (I²C)
```

El *power path* permite operar desde el USB mientras la batería carga. Sin él, un
dispositivo que se usa conectado nunca termina de cargar y el riel de sistema cae.

## Cadena de video

```
cámara CSI ──▶ Pi (H.264 por hardware) ──▶ RTMP ──▶ plataforma
```

Un solo codificado. Por eso el prototipo usa cable en lugar de radio: cualquier enlace
inalámbrico desde los lentes obligaría a un segundo codificado o a enviar JPEG.

## Presupuesto de ancho de banda (30 fps)

| Configuración | Mbps | Veredicto |
|---|---|---|
| 480p JPEG | 9.2 | al límite del WiFi de un ESP32-S3 |
| 480p H.264 | 1.0 | holgado |
| 720p JPEG | 27.6 | imposible por WiFi |
| 720p H.264 | 3.0 | holgado |
| 1080p H.264 | 6.8 | pasa |

## Térmica

Red de 3 nodos (Pi → carcasa → ambiente/cuerpo) a 2.5 W, ambiente 25 °C, piel 33 °C:

| Escenario | Pi | Carcasa |
|---|---|---|
| Cuerpo, sin ventilación | 45.4 °C | 37.9 °C |
| Cuerpo, con ventilación | 43.6 °C | 36.1 °C |
| Ventilación + disipador de aluminio | 38.8 °C | 35.0 °C |

La carcasa se mantiene debajo del límite de confort de 45 °C. A 35 °C de ambiente sube
unos 10 K, así que en verano o bajo el sol conviene llevarla cubierta por la ropa.

## Riesgos abiertos

1. El cable CSI se degrada pasados ~50 cm: la unidad va en hombro, pecho o bandolera.
2. Micrófono compartido: definir si el agente escucha durante un directo.
3. Elegibilidad de la cuenta para transmisión por RTMP en algunas plataformas.
4. Homologación del módem celular para un producto comercial.

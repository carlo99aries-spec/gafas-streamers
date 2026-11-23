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

## Salidas de video — tres destinos, un sensor

El mismo sensor alimenta tres rutas simultáneas con un `tee`:

| Modo | Protocolo | Latencia | Para qué |
|---|---|---|---|
| Directo público | RTMP | 2–6 s | TikTok, Facebook, YouTube |
| Vista privada | WebRTC | < 1 s | monitor propio, productor, cliente |
| Tap para el agente | JPEG ~1 fps | n/a | visión para el asistente |

La visión del agente **no compite** con el directo: 1 fps de JPEG pesa ~40 KB/s contra
3 Mbps del video. Un agente no necesita 30 fps para entender una escena; los necesita
para transmitirla.

WebRTC abre un modo que RTMP no puede dar: latencia menor a un segundo para un viewer
privado. Útil para revisar el encuadre tú mismo o para que alguien te dirija el directo.

## Audio — dos caminos

| Camino | Latencia típica | Cuándo usarlo |
|---|---|---|
| Nativo en tiempo real | 0.6–1.0 s | por defecto |
| STT → LLM → TTS | 1.5–3 s | fallback, o modelos locales |

Los modelos nativos de audio (Gemini Live, OpenAI Realtime) reciben y emiten audio por
un WebSocket, sin pasar por texto. Eso elimina dos saltos del camino y baja la sensación
de conversación por debajo del segundo.

El costo de ancho de banda es despreciable: 32 KB/s de subida y 48 KB/s de bajada,
frente a los 3 Mbps del video.

**Requisito:** el fallback STT/TTS debe existir. Los modelos nativos dependen de la nube
y de la latencia de red; si el enlace se degrada, la voz tiene que seguir funcionando.

## Prior art

[VisionClaw](https://github.com/Intent-Lab/VisionClaw) demuestra este patrón sobre
Meta Ray-Ban: video a ~1 fps hacia Gemini Live, audio nativo bidireccional y llamadas de
herramientas contra OpenClaw. Sirve como validación de que 1 fps basta para visión y de
que el audio nativo es el camino correcto. No se reutiliza su código: su licencia no es
clara y está atado al SDK de Meta.

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

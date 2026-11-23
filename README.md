# Gafas Streamers

Lentes con cámara para transmitir en vivo a redes sociales, con canal de voz bidireccional
hacia un agente de IA.

Diseño abierto de hardware: dos módulos portados, unidos por un cable plano.

```
┌──────────────────────────┐                      ┌────────────────────────────┐
│  LENTES                  │   cable FFC ≤ 50 cm  │  UNIDAD                    │
│  cámara CSI              │─────────────────────▶│  Raspberry Pi Zero 2 W     │
│  2 micrófonos I2S        │                      │  módem LTE (EC25)          │
│  altavoz + LED           │                      │  batería LiPo 4000 mAh     │
│  ~35 g                   │                      │  ~150 g                    │
└──────────────────────────┘                      └────────────────────────────┘
                                                              │
                                             RTMP ──▶ TikTok / Facebook / YouTube
                                             WebSocket ──▶ agente de IA
```

## La idea

Dos objetivos, una sola cámara:

1. **Directo.** Activar el stream y estar en vivo en cualquier momento: calle, parque,
   casa, trabajo. Sin trípode, sin manos, sin equipo.
2. **Asistente.** Hablar con el agente donde esté alojado, estilo Jarvis: respuesta al
   oído, y visión — la cámara también le manda el cuadro al agente.

La cámara es **salida** para el directo y **entrada** para el agente. El directo hace que
lo compres; el asistente hace que lo traigas puesto.

## Arquitectura

Los lentes son **una cabeza de sensores**: sin batería, sin radio, sin cómputo.
La unidad es **el cuerpo**: cómputo, batería y enlace celular.

Esa separación resuelve los tres problemas clásicos de un wearable:

| Problema | Cómo se resuelve |
|---|---|
| Peso en la cara | solo cámara, mics, altavoz y LED: ~35 g |
| Calor junto a la sien | no hay procesador en el armazón |
| Autonomía de los lentes | no hay batería: duran lo que dure la unidad |

## Números del diseño

Validados por simulación (ver `sim/`):

| Métrica | Valor |
|---|---|
| Convertidor boost 3.7 → 5 V | rizo 10.2 mV pp, duty 26.5 % |
| Eficiencia del boost | 98.2 % (techo, sin pérdidas de conmutación) |
| Temperatura de carcasa a 2.5 W | 37.9 °C (ambiente 25 °C) |
| Autonomía de la unidad | 4.9 h con 4000 mAh |
| Video 720p30 H.264 | 3.0 Mbps |
| Video 720p30 JPEG | 27.6 Mbps — no pasa el WiFi |

## Decisiones de ingeniería

| Tema | Decisión | Por qué |
|---|---|---|
| Cargador | BQ25895 | *power path*: el sistema corre del USB mientras carga |
| Módem | Quectel EC25 por USB (mini-PCIe) | USB 2.0 nativo; evita soldar LCC de 2.6 mm |
| Raspberry Pi | Zero 2 W, **sin header** | el header no cabe: 8.5–11 mm contra ~6 mm de cavidad |
| Cámara | CSI + cable en V1 | encoda H.264 por hardware, sin transcode doble |

**Hallazgo importante:** un ESP32-S3 no puede encodificar H.264, así que obliga a enviar
JPEG. Eso pone el techo del sistema en 480p30, no en la Raspberry Pi (que sí tiene encoder
por hardware). Para un producto en 720p/1080p habría que cambiar el SoC de los lentes.

## Estructura del repositorio

```
cad/          modelos paramétricos en OpenSCAD
  unidad.scad   carcasa de la unidad (78 × 64 × 22 mm)
  lentes.scad   armazón de los lentes (138 × 46 mm)
tools/
  gen_sch.py    genera el esquemático de sistema en formato KiCad
sim/
  sim_power.py   simulación conmutada del boost
  sim_thermal.py red térmica de 3 nodos
  sim_video.py   presupuesto de ancho de banda de video
docs/
  ARQUITECTURA.md
  BOM-V1.md
```

Los STL, PNG y el `.kicad_sch` **no se versionan**: se generan con los scripts.

## Uso

### Modelos 3D

```bash
openscad -o unidad.stl cad/unidad.scad
openscad -o lentes.stl  cad/lentes.scad
```

Ambos modelos son paramétricos: todas las medidas están al inicio del archivo.

### Esquemático

```bash
python tools/gen_sch.py                       # escribe sistema.kicad_sch
kicad-cli sch export svg sistema.kicad_sch -o svg_out
```

### Simulaciones

```bash
python sim/sim_power.py     # etapa de potencia
python sim/sim_thermal.py   # térmica
python sim/sim_video.py     # ancho de banda de video
```

Requiere Python 3 con `numpy`, `scipy` y `matplotlib`.

## Requisitos

- [OpenSCAD](https://openscad.org/) 2021.01 o superior
- [KiCad](https://www.kicad.org/) 9 o superior (para `kicad-cli`)
- Python 3.10+ con numpy, scipy, matplotlib

## Estado

Prototipo conceptual. Diseño cerrado, CAD y simulaciones hechas. Falta construir y medir
el comportamiento real: decodificar JPEG, encodificar H.264 y subir por LTE al mismo
tiempo es lo que ninguna simulación puede probar.

## Licencia

MIT. Ver [LICENSE](LICENSE).

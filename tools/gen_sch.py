#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del esquema de sistema de Gafas Streamers.
Emite un .kicad_sch valido (KiCad 10 / version 20250114).

Uso:  python gen_sch.py
Salida: sistema.kicad_sch
"""

import uuid
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sistema.kicad_sch")

def U():
    return str(uuid.uuid4())

# ---------------------------------------------------------------- bloques
# (x, y, w, h, titulo, subtitulo, [pines])
# pin = (lado, fraccion_vertical, nombre_net)
B = [
    (20, 52, 56, 46, "USB-C", "PD 5V 3A",
     [("right", 0.30, "VBUS"), ("right", 0.70, "GND")]),

    (92, 52, 66, 46, "Carga BQ25895", "power path + I2C",
     [("left", 0.30, "VBUS"), ("left", 0.70, "GND"),
      ("right", 0.28, "VBAT"), ("right", 0.62, "SYS"), ("right", 0.88, "I2C")]),

    (176, 52, 56, 46, "BATERIA", "4000 mAh LiPo",
     [("left", 0.30, "VBAT"), ("left", 0.70, "GND"),
      ("bottom", 0.5, "I2C")]),

    (250, 52, 62, 46, "BOOST 5V", "TPS61088",
     [("left", 0.30, "SYS"), ("left", 0.70, "GND"),
      ("right", 0.50, "5V")]),

    (328, 44, 80, 62, "Pi Zero 2 W", "sin header",
     [("left", 0.25, "5V"), ("left", 0.60, "GND"),
      ("right", 0.30, "USB2"), ("right", 0.68, "WIFI")]),

    (176, 146, 56, 42, "Fuel gauge", "MAX17048",
     [("top", 0.5, "I2C")]),

    (250, 140, 60, 44, "HUB USB2", "SL2.1A",
     [("left", 0.35, "USB2"), ("left", 0.75, "GND"),
      ("right", 0.50, "USBM")]),

    (328, 134, 80, 52, "MODEM LTE", "EC25 mini-PCIe",
     [("left", 0.30, "USBM"), ("left", 0.70, "GND")]),

    (328, 206, 80, 46, "LENTES ESP32-S3", "camara + audio",
     [("left", 0.30, "WIFI"), ("left", 0.70, "GND")]),
]

def rect(x, y, w, h):
    return (f'\t(rectangle\n'
            f'\t\t(start {x} {y})\n'
            f'\t\t(end {x+w} {y+h})\n'
            f'\t\t(stroke (width 0.25) (type solid))\n'
            f'\t\t(fill (type none))\n'
            f'\t\t(uuid "{U()}")\n'
            f'\t)\n')

def text(x, y, s, size=1.6, bold=True):
    b = " (bold yes)" if bold else ""
    return (f'\t(text "{s}"\n'
            f'\t\t(at {x} {y} 0)\n'
            f'\t\t(effects (font (size {size} {size}){b}) (justify left bottom))\n'
            f'\t\t(uuid "{U()}")\n'
            f'\t)\n')

def glabel(x, y, net, rot, shape):
    return (f'\t(global_label "{net}"\n'
            f'\t\t(shape {shape})\n'
            f'\t\t(at {x} {y} {rot})\n'
            f'\t\t(fields_autoplaced yes)\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify {"right" if rot==180 else "left"}))\n'
            f'\t\t(uuid "{U()}")\n'
            f'\t)\n')

body = []
for (x, y, w, h, title, sub, pins) in B:
    body.append(rect(x, y, w, h))
    body.append(text(x + 4, y + 9, title, 1.7, True))
    body.append(text(x + 4, y + 15.5, sub, 1.1, False))
    for (side, frac, net) in pins:
        if side == "right":
            px, py = x + w, y + h * frac
            body.append(glabel(px, py, net, 0, "output"))
        elif side == "left":
            px, py = x, y + h * frac
            body.append(glabel(px, py, net, 180, "input"))
        elif side == "bottom":
            px, py = x + w * frac, y + h
            body.append(glabel(px, py, net, 270, "input"))
        elif side == "top":
            px, py = x + w * frac, y
            body.append(glabel(px, py, net, 90, "output"))

doc = []
doc.append('(kicad_sch\n')
doc.append('\t(version 20250114)\n')
doc.append('\t(generator "eeschema")\n')
doc.append('\t(generator_version "9.0")\n')
doc.append(f'\t(uuid "{U()}")\n')
doc.append('\t(paper "A3")\n')
doc.append('\t(title_block\n')
doc.append('\t\t(title "Gafas Streamers - arquitectura electrica")\n')
doc.append('\t\t(rev "A")\n')
doc.append('\t\t(comment 1 "Generado por gen_sch.py - editar el script, no el archivo")\n')
doc.append('\t)\n')
doc.append('\t(lib_symbols)\n')
doc.extend(body)
doc.append('\t(sheet_instances\n')
doc.append('\t\t(path "/"\n')
doc.append('\t\t\t(page "1")\n')
doc.append('\t\t)\n')
doc.append('\t)\n')
doc.append('\t(embedded_fonts no)\n')
doc.append(')\n')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("".join(doc))

print("escrito:", OUT)
print("bloques:", len(B))

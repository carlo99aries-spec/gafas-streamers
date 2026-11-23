#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Presupuesto de video de Gafas Streamers.
Compara el ancho de banda que exige cada configuracion contra la capacidad
real del enlace lentes->unidad (WiFi del ESP32-S3) y del enlace a internet (LTE).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sim_video.png")

# ---------------------------------------------------------------- enlaces
WIFI_ESP32 = 11.0      # Mbps sostenidos reales con el SoC ocupado
LTE_BIEN = 14.0        # Mbps subida en celda descongestionada
LTE_MAL = 3.5          # Mbps subida en celda congestionada

RES = {
    "480p  (640x480)":   (640, 480),
    "720p  (1280x720)":  (1280, 720),
    "1080p (1920x1080)": (1920, 1080),
}

# bits por pixel tipicos
BPP = {
    "JPEG q12":  1.00,
    "JPEG q18":  0.62,
    "H.264":     0.11,
}

def mbps(w, h, bpp, fps):
    return w * h * bpp * fps / 1e6

escenarios = []
for rname, (w, h) in RES.items():
    for cname, bpp in BPP.items():
        for fps in (30,):
            escenarios.append((rname, cname, fps, mbps(w, h, bpp, fps)))

print("=" * 72)
print("%-22s %-11s %5s %10s   %s" % ("Resolucion", "Codec", "fps", "Mbps", "Veredicto"))
print("=" * 72)
for rname, cname, fps, m in escenarios:
    if m > WIFI_ESP32:
        v = "NO pasa el WiFi"
    elif m > LTE_MAL:
        v = "cabe en WiFi, sufre en LTE malo"
    else:
        v = "holgado"
    print("%-22s %-11s %5d %10.1f   %s" % (rname, cname, fps, m, v))

# ---------------------------------------------------------------- grafica
plt.style.use("dark_background")
fig, ax = plt.subplots(1, 2, figsize=(13.4, 5.4), dpi=130)
fig.patch.set_facecolor("#0b1018")

for a in ax:
    a.set_facecolor("#111a26")
    a.tick_params(colors="#8b9db8", labelsize=9)
    for s in a.spines.values():
        s.set_color("#25344a")
    a.grid(color="#1e2b3d", linewidth=0.7, axis="y")

# panel 1: barras por escenario
labels = ["%s\n%s" % (r.split()[0], c) for (r, c, f, m) in escenarios]
vals = [m for (_, _, _, m) in escenarios]
cols = []
for (_, c, _, m) in escenarios:
    if m > WIFI_ESP32:
        cols.append("#e0524d")
    elif m > LTE_MAL:
        cols.append("#f0b429")
    else:
        cols.append("#3fbf74")

x = np.arange(len(vals))
ax[0].bar(x, vals, color=cols, width=0.68)
ax[0].axhline(WIFI_ESP32, color="#4dd6ff", ls="--", lw=1.2, label="WiFi ESP32-S3 (~11 Mbps)")
ax[0].axhline(LTE_MAL, color="#9b8cff", ls=":", lw=1.2, label="LTE congestionado (~3.5 Mbps)")
ax[0].set_xticks(x)
ax[0].set_xticklabels(labels, fontsize=7.2, rotation=0)
ax[0].set_ylabel("Mbps", color="#8b9db8")
ax[0].set_title("Ancho de banda requerido a 30 fps", color="#e9eff8", fontsize=11)
ax[0].legend(fontsize=8, facecolor="#111a26", edgecolor="#25344a")

# panel 2: fps alcanzable por resolucion y codec bajo WiFi
fps_axis = np.arange(5, 61, 1)
for cname in ("JPEG q12", "JPEG q18", "H.264"):
    bpp = BPP[cname]
    for rname, (w, h) in RES.items():
        if rname.startswith("480p") or rname.startswith("720p"):
            fmax = WIFI_ESP32 * 1e6 / (w * h * bpp)
            ls = "-" if rname.startswith("480p") else "--"
            ax[1].plot(fps_axis, [mbps(w, h, bpp, f) for f in fps_axis],
                       lw=1.5, ls=ls,
                       color={"JPEG q12": "#e0524d", "JPEG q18": "#f0b429", "H.264": "#3fbf74"}[cname],
                       alpha=0.95 if cname == "H.264" else 0.75)
    ax[1].plot([], [], color={"JPEG q12": "#e0524d", "JPEG q18": "#f0b429", "H.264": "#3fbf74"}[cname],
               lw=1.5, label=cname)

ax[1].axhline(WIFI_ESP32, color="#4dd6ff", ls="--", lw=1.2, label="WiFi ESP32-S3")
ax[1].axhline(LTE_MAL, color="#9b8cff", ls=":", lw=1.2, label="LTE congestionado")
ax[1].axvline(30, color="#8b9db8", ls=":", lw=0.8)
ax[1].text(30.6, ax[1].get_ylim()[1] * 0.92, "30 fps", color="#8b9db8", fontsize=8)
ax[1].set_xlabel("fps", color="#8b9db8")
ax[1].set_ylabel("Mbps", color="#8b9db8")
ax[1].set_title("Linea solida = 480p · discontinua = 720p", color="#a8b8cc", fontsize=9.5)
ax[1].set_ylim(0, max(45, WIFI_ESP32 * 1.3))
ax[1].legend(fontsize=8, facecolor="#111a26", edgecolor="#25344a")

fig.tight_layout(pad=1.6)
fig.savefig(OUT, facecolor=fig.get_facecolor())
plt.close(fig)

print()
print("WiFi sostenido ESP32-S3 asumido : %.1f Mbps" % WIFI_ESP32)
print("LTE subida (celda buena / mala) : %.1f / %.1f Mbps" % (LTE_BIEN, LTE_MAL))
print("grafica:", OUT)

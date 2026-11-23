#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo termico de la unidad (Modulo B).
Red de 3 nodos: Pi (fuente) -> carcasa -> ambiente / cuerpo.
Compara escenarios y barre potencia.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sim_thermal.png")

# ---------------------------------------------------------------- constantes
T_AMB = 25.0      # C ambiente
T_BODY = 33.0     # C piel con ropa ligera

C_PI = 5.0        # J/K  masa termica del Pi + PCB
C_CASE = 60.0     # J/K  carcasa PETG
C_BAT = 120.0     # J/K  celda LiPo

R_PI_CASE = 3.0   # K/W  Pi -> carcasa (aire interno)
R_BAT_CASE = 2.5  # K/W  bateria -> carcasa

def simulate(P, r_amb, r_body, r_pi_case=R_PI_CASE, t_end=2400.0, dt=0.5):
    n = int(t_end / dt)
    tpi = tcase = tbat = T_AMB
    out = np.empty((n, 4))
    for i in range(n):
        q_pi = (tpi - tcase) / r_pi_case
        q_ca = (tcase - T_AMB) / r_amb
        q_cb = (tcase - T_BODY) / r_body if r_body else 0.0
        q_bat = (tcase - tbat) / R_BAT_CASE

        tpi += (P - q_pi) / C_PI * dt
        tcase += (q_pi - q_ca - q_cb) / C_CASE * dt
        tbat += q_bat / C_BAT * dt
        out[i] = (i * dt / 60.0, tpi, tcase, tbat)
    return out

def steady(P, r_amb, r_body, r_pi_case=R_PI_CASE):
    # resolver el sistema lineal en regimen
    # (T_pi-T_c)/Rp = P ; (T_c-T_a)/Ra + (T_c-T_b)/Rb + (T_c-T_bat)/Rbat = (T_pi-T_c)/Rp
    g1 = 1.0 / r_pi_case
    ga = 1.0 / r_amb
    gb = (1.0 / r_body) if r_body else 0.0
    gx = 1.0 / R_BAT_CASE
    # incognitas T_pi, T_c, T_bat
    A = np.array([
        [g1, -g1, 0.0],
        [-g1, g1 + ga + gb + gx, -gx],
        [0.0, -gx, gx],
    ])
    b = np.array([P, ga * T_AMB + gb * T_BODY, 0.0])
    return np.linalg.solve(A, b)

# ---------------------------------------------------------------- escenarios
ESC = [
    ("Cuerpo, sin ventilacion", 10.0, 4.0, R_PI_CASE, "#e0524d"),
    ("Cuerpo, con ventilacion", 6.5, 4.0, R_PI_CASE, "#f0b429"),
    ("Ventilacion + disipador Al", 5.0, 4.0, 1.5, "#3fbf74"),
]
P_UNIT = 2.5

plt.style.use("dark_background")
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), dpi=130)
fig.patch.set_facecolor("#0b1018")

curves = []
for name, ra, rb, rp, col in ESC:
    d = simulate(P_UNIT, ra, rb, rp)
    curves.append((name, d, col))
    st = steady(P_UNIT, ra, rb, rp)
    print("%-30s  Pi %.1f C | carcasa %.1f C | bat %.1f C" % (name, st[0], st[1], st[2]))

for a in ax:
    a.set_facecolor("#111a26")
    a.tick_params(colors="#8b9db8", labelsize=9)
    for s in a.spines.values():
        s.set_color("#25344a")
    a.grid(color="#1e2b3d", linewidth=0.7)

for name, d, col in curves:
    ax[0].plot(d[:, 0], d[:, 1], color=col, lw=1.8, label=name)
ax[0].axhline(45, color="#ffffff", ls=":", lw=1.0)
ax[0].text(2, 45.6, "limite de contacto 45 C", color="#c9d6e8", fontsize=8)
ax[0].set_title("Temperatura del Pi a 2.5 W", color="#e9eff8", fontsize=11)
ax[0].set_xlabel("minutos", color="#8b9db8")
ax[0].set_ylabel("C", color="#8b9db8")
ax[0].legend(fontsize=8, facecolor="#111a26", edgecolor="#25344a")

ps = np.linspace(1.0, 3.5, 26)
for name, ra, rb, rp, col in ESC:
    vals = [steady(p, ra, rb, rp)[1] for p in ps]
    ax[1].plot(ps, vals, color=col, lw=1.8, label=name)
ax[1].axhline(45, color="#ffffff", ls=":", lw=1.0)
ax[1].axvline(P_UNIT, color="#4dd6ff", ls="--", lw=0.9)
ax[1].text(P_UNIT + 0.05, 28, "2.5 W", color="#4dd6ff", fontsize=8)
ax[1].set_title("Carcasa en regimen vs potencia", color="#e9eff8", fontsize=11)
ax[1].set_xlabel("W", color="#8b9db8")
ax[1].set_ylabel("C", color="#8b9db8")
ax[1].legend(fontsize=8, facecolor="#111a26", edgecolor="#25344a")

fig.tight_layout(pad=1.6)
fig.savefig(OUT, facecolor=fig.get_facecolor())
plt.close(fig)

st = steady(P_UNIT, 10.0, 4.0, R_PI_CASE)
print()
print("Sin ventilacion, carcasa a %.1f C -> %s" % (
    st[1], "EXCEDE el limite de 45 C" if st[1] > 45 else "dentro del limite"))
print("grafica:", OUT)

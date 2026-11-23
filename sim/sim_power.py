#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulacion de la etapa de potencia de Gafas Streamers  (v2, corregida)
- Convertidor boost conmutado con control PI actualizado UNA vez por ciclo
- Rectificacion sincrona (sin caida de diodo)
- Modelo de descarga de bateria LiPo 1S
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sim_power.png")

# ---------------------------------------------------------------- parametros
VIN = 3.7
VREF = 5.0
FSW = 700e3
TSW = 1.0 / FSW
L = 2.2e-6
RL = 0.015         # DCR inductor
RDS = 0.020        # Rds(on) sincrono
COUT = 94e-6
RLOAD = VREF / 2.5

DT = 1e-8
TEND = 4e-3
N = int(TEND / DT)

# ---------------------------------------------------------------- lazo
D = 0.26
integ = 0.0
KP, KI = 0.06, 8.0
D_NOM = 0.26
next_upd = 0.0

iL = 0.0
vC = VIN
t = 0.0

ts, vs, ils, ds = [], [], [], []
tail_t, tail_v, tail_i = [], [], []
TAIL = 200e-6

for k in range(N):
    if t >= next_upd:
        err = VREF - vC
        integ = min(max(integ + err * TSW, -3.0), 3.0)
        D = D_NOM + KP * err + KI * integ
        D = min(max(D, 0.05), 0.85)
        next_upd = t + TSW

    phase = (t * FSW) % 1.0
    on = phase < D

    if on:
        di = (VIN - iL * (RL + RDS)) / L
        dvc = -vC / (RLOAD * COUT)
    else:
        di = (VIN - iL * RL - vC) / L
        dvc = (iL - vC / RLOAD) / COUT

    iL += di * DT
    vC += dvc * DT
    if iL < 0: iL = 0.0
    t += DT

    if k % 20 == 0:
        ts.append(t * 1e3); vs.append(vC); ils.append(iL); ds.append(D)
    if t > TEND - TAIL:
        tail_t.append(t * 1e6); tail_v.append(vC); tail_i.append(iL)

ts = np.array(ts); vs = np.array(vs); ils = np.array(ils); ds = np.array(ds)
tail_t = np.array(tail_t); tail_v = np.array(tail_v); tail_i = np.array(tail_i)

# ---------------------------------------------------------------- metricas
n_last = max(len(vs) // 4, 200)
vout_avg = float(np.mean(tail_v))
vout_ripple = float(np.max(tail_v) - np.min(tail_v))
iL_avg = float(np.mean(tail_i))
iL_ripple = float(np.max(tail_i) - np.min(tail_i))
duty = float(np.mean(ds[-n_last:]))
vout_drift = float(np.max(vs[-n_last:]) - np.min(vs[-n_last:]))

pin = VIN * iL_avg
pout = vout_avg * iL_avg * (1 - duty) if iL_avg > 0 else 0.0
pout = vout_avg ** 2 / RLOAD
eff = 100.0 * pout / pin if pin > 0 else 0.0

# ---------------------------------------------------------------- bateria
def battery_run(p_watts, cap_mah, v_cut=3.30, rint=0.080):
    soc = 1.0
    cap_c = cap_mah * 3.6
    t_s = 0.0
    dtb = 5.0
    tr = []
    while t_s < 24 * 3600 and soc > 0:
        ocv = 3.00 + 1.20 * (soc ** 0.70)
        i = p_watts / max(ocv, 3.0)
        v = ocv - i * rint
        if v <= v_cut:
            break
        soc -= (i * dtb) / cap_c
        if soc < 0: soc = 0
        t_s += dtb
        if int(t_s) % 600 < dtb:
            tr.append((t_s / 3600.0, v, soc * 100))
    tr.append((t_s / 3600.0, v, soc * 100))
    return t_s / 3600.0, np.array(tr)

h_unit, tr_unit = battery_run(2.5 / (eff / 100.0), 4000)
h_lens, tr_lens = battery_run(0.40, 180, rint=0.150)

# ---------------------------------------------------------------- graficas
plt.style.use("dark_background")
fig, ax = plt.subplots(2, 2, figsize=(13, 8.2), dpi=130)
fig.patch.set_facecolor("#0b1018")
acc = "#4dd6ff"; acc2 = "#9b8cff"; gd = "#f0b429"; gr = "#3fbf74"

for a in ax.flat:
    a.set_facecolor("#111a26")
    a.tick_params(colors="#8b9db8", labelsize=9)
    for s in a.spines.values():
        s.set_color("#25344a")
    a.grid(color="#1e2b3d", linewidth=0.7)

ax[0][0].plot(ts, vs, color=acc, lw=1.2)
ax[0][0].axhline(VREF, color=gd, ls="--", lw=0.9, label="objetivo 5.0 V")
ax[0][0].set_title("Arranque: Vout vs tiempo", color="#e9eff8", fontsize=11)
ax[0][0].set_xlabel("ms", color="#8b9db8"); ax[0][0].set_ylabel("V", color="#8b9db8")
ax[0][0].legend(fontsize=8, facecolor="#111a26", edgecolor="#25344a")

ax[0][1].plot(tail_t, tail_v, color=acc2, lw=1.1)
ax[0][1].set_title("Rizo en regimen: %.1f mV pp" % (vout_ripple * 1000), color="#e9eff8", fontsize=11)
ax[0][1].set_xlabel("us", color="#8b9db8"); ax[0][1].set_ylabel("V", color="#8b9db8")

ax[1][0].plot(ts, ils, color=gd, lw=1.0)
ax[1][0].set_title("Corriente en el inductor: %.2f A pp" % iL_ripple, color="#e9eff8", fontsize=11)
ax[1][0].set_xlabel("ms", color="#8b9db8"); ax[1][0].set_ylabel("A", color="#8b9db8")

ax[1][1].plot(tr_unit[:, 0], tr_unit[:, 1], color=gr, lw=1.8, label="unidad 4000 mAh")
if len(tr_lens) > 1:
    ax[1][1].plot(tr_lens[:, 0], tr_lens[:, 1], color="#e0524d", lw=1.8, label="lentes 180 mAh")
ax[1][1].axhline(3.3, color="#8b9db8", ls=":", lw=0.9, label="corte 3.3 V")
ax[1][1].set_title("Descarga de bateria", color="#e9eff8", fontsize=11)
ax[1][1].set_xlabel("horas", color="#8b9db8"); ax[1][1].set_ylabel("V", color="#8b9db8")
ax[1][1].legend(fontsize=8, facecolor="#111a26", edgecolor="#25344a")

fig.tight_layout(pad=1.6)
fig.savefig(OUT, facecolor=fig.get_facecolor())
plt.close(fig)

print("=" * 58)
print("CONVERTIDOR BOOST  (Vin 3.7 V -> Vout 5.0 V @ 2.5 A)")
print("=" * 58)
print("  Vout promedio      : %8.3f V" % vout_avg)
print("  Rizo de salida     : %8.1f mV pp" % (vout_ripple * 1000))
print("  Deriva lenta (1ms) : %8.1f mV" % (vout_drift * 1000))
print("  Duty promedio      : %8.1f %%" % (duty * 100))
print("  iL promedio        : %8.2f A" % iL_avg)
print("  iL rizo            : %8.2f A pp" % iL_ripple)
print("  Pin / Pout         : %8.2f W / %.2f W" % (pin, pout))
print("  Eficiencia         : %8.1f %%" % eff)
print()
print("=" * 58)
print("AUTONOMIA")
print("=" * 58)
print("  Unidad 4000 mAh    : %8.2f h  (carga 2.5 W)" % h_unit)
print("  Lentes  180 mAh    : %8.2f h  (carga 0.40 W)" % h_lens)
print()
print("grafica:", OUT)

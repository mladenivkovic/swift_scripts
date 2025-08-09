#!/usr/bin/env python3

# Reads in "statistics.txt" and plots all masses over time.

from swiftsimio import load_statistics
from matplotlib import pyplot as plt

data = load_statistics("statistics.txt")

plotkwargs = {"linestyle": "--", "alpha": 0.6}

times = data.time

mtot = data.total_mass
mgas = data.gas_mass
mstars = data.star_mass
msinks = data.sink_mass
mbh = data.bh_mass


has_gas = False
has_stars = False
has_sinks = False
has_bh = False

if mgas.any():
    has_gas = True

if mstars.any():
    has_stars = True

if msinks.any():
    has_sinks = True

if mbh.any():
    has_bh = True


fig = plt.figure(figsize=(8, 4), dpi=200)
ax = fig.add_subplot(111)
if has_gas:
    ax.plot(times, mgas, label="gas", **plotkwargs)
if has_stars:
    ax.plot(times, mstars, label="stars", **plotkwargs)
if has_sinks:
    ax.plot(times, msinks, label="sinks", **plotkwargs)
if has_bh:
    ax.plot(times, mbh, label="BH", **plotkwargs)
ax.plot(times, mtot, "r", label="total mass")
ax.legend()
ax.set_xlabel("Time")
ax.set_ylabel("Masses")

plt.savefig("mass_statistics.png")

print(
    "| 1 - M_tot_initial / M_tot_final| = {0:.6f}".format(abs(1 - mtot[0] / mtot[-1]))
)
print(
    "| 1 - M_gas_initial / M_gas_final| = {0:.6f}".format(abs(1 - mgas[0] / mgas[-1]))
)

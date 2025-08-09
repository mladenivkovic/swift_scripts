#!/usr/bin/env python3

# Reads in "statistics.txt" and plots gas mass and energies over time.

from swiftsimio import load_statistics
from matplotlib import pyplot as plt

data = load_statistics("statistics.txt")

times = data.time
mass = data.gas_mass
ekin = data.kin_energy
eu = data.int_energy
epot = data.pot_energy
etot = ekin + eu + epot


fig = plt.figure(figsize=(8, 4), dpi=200)
ax = fig.add_subplot(111)
ax.plot(times, mass, "r--", label="gas mass")
ax.plot(times, etot, "b", label="E_kin + E_int + E_pot")
ax.plot(times, ekin, ":", label="E_kin", alpha = 0.6)
ax.plot(times, eu, ":", label="E_int", alpha = 0.6)
ax.plot(times, epot, ":", label="E_pot", alpha = 0.6)
ax.legend()
ax.set_xlabel("Time")
ax.set_ylabel("Energies")

plt.savefig("gas_statistics.png")

print(
    "| 1 - E_tot_initial / E_tot_final| = {0:.6f}".format(abs(1 - etot[0] / etot[-1]))
)

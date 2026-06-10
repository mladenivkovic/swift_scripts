#!/usr/bin/env python3

from swift_hardcoded_data import timer_names

import matplotlib

matplotlib.use("Agg")

import argparse
import os
import numpy as np
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(
    prog="plotGPUtimers.py",
    description="plot the outputs of the timers.",
    epilog="To get timers output with swift, first configure with `./configure --enable-timers` and then run swift with `./swift --timers`",
)

parser.add_argument(
    "timer_file",
    nargs="?",
    action="store",
    default="timers_0.txt",
    help="file to read in. Default: 'timers_0.txt'",
    type=str,
)

parser.add_argument(
    "-n",
    "--nthreads",
    action="store",
    default=1,
    type=int,
    help="normalise timers assuming N threads",
)
parser.add_argument(
    "-s",
    "--seconds",
    action="store_true",
    help="use seconds as units, not milliseconds",
)
parser.add_argument(
    "-z",
    "--include-step-zero",
    action="store_true",
    help="Include the zeroth step in the timing averages",
)

args = parser.parse_args()
nthreads = args.nthreads
units = "ms"
if args.seconds:
    units = "s"

if not os.path.exists(args.timer_file):
    print(f"Couldn't find timer file {args.timer_file}.")
    exit(1)

# Which data do we include in the averages?
first_index = 1
if args.include_step_zero:
    first_index = 0


cols_to_use = []
# add +1: 0th column in `timer_names` is "step"
cols_to_use.append(timer_names.index("gpu_pack_density") + 1)
cols_to_use.append(timer_names.index("gpu_pack_gradient") + 1)
cols_to_use.append(timer_names.index("gpu_pack_force") + 1)
cols_to_use.append(timer_names.index("gpu_unpack_density") + 1)
cols_to_use.append(timer_names.index("gpu_unpack_gradient") + 1)
cols_to_use.append(timer_names.index("gpu_unpack_force") + 1)
cols_to_use.append(timer_names.index("gpu_launch_density") + 1)
cols_to_use.append(timer_names.index("gpu_launch_gradient") + 1)
cols_to_use.append(timer_names.index("gpu_launch_force") + 1)
cols_to_use.append(timer_names.index("gpu_self_recurse") + 1)
cols_to_use.append(timer_names.index("gpu_pair_recurse") + 1)

# Load data
data = np.loadtxt(args.timer_file, usecols=cols_to_use)
if nthreads > 1:
    print(f"Normalising times assuming {nthreads} threads")
    data /= nthreads
if args.seconds:
    data *= 1e-3

# Print values to screen
timesum_avg = 0.0
timesum_total = 0.0

print()
print("Times averaged over all available measured steps:")
if nthreads <= 1:
    print("{0:25} {1:>18s}".format("Task Type", f"Total time {units}"))

    for i, col in enumerate(cols_to_use):
        avg = data[first_index:, i].mean()
        name = timer_names[col - 1]  # subtract 1 to get the index in my hand-made list

        print("{0:25} {1:18.3e}".format(name, avg))
        timesum_avg += avg

    print()
    print(f"Total: {timesum_avg:18.3e} {units}")

else:
    print(
        "{0:25} {1:>18} {2:>18}".format(
            "Task Type", f"Avg. Time {nthreads} thr", f"Total time {units}"
        )
    )

    for i, col in enumerate(cols_to_use):
        avg = data[first_index:, i].mean()
        name = timer_names[col - 1]  # subtract 1 to get the index in my hand-made list

        print("{0:25} {1:18.3e} {2:18.3e}".format(name, avg, avg * nthreads))
        timesum_avg += avg
        timesum_total += avg * nthreads

    print()
    print(f"Total: All threads:     {timesum_total:18.3e} {units}")
    print(f"       Avg. per thread: {timesum_avg:18.3e} {units}")
print()


# Make plot

fig = plt.figure(figsize=(5, 5), dpi=200)

ax = fig.add_subplot(111)
for i, col in enumerate(cols_to_use):
    avg = data[first_index:, i].mean()
    minval = data[first_index:, i].min()
    maxval = data[first_index:, i].max()
    name = timer_names[col - 1]  # subtract 1 to get the index in my hand-made list
    color = "C0"
    if "_pack_" in name:
        color = "C0"
    if "_unpack_" in name:
        color = "C1"
    if "launch" in name:
        color = "C2"
    if "recurse" in name:
        color = "C3"
    ax.errorbar(
        name,
        avg,
        yerr=[[avg - minval], [maxval - avg]],
        c=color,
        capsize=4,
        fmt="o",
        markersize=4,
    )

if nthreads <= 1:
    ax.set_ylabel(f"Task times [{units}] summed over all threads")
else:
    ax.set_ylabel(f"Task times [{units}] averaged per thread ({nthreads} total)")

locs = ax.get_xticks()
labels = ax.get_xticklabels()
ax.set_xticks(locs, labels, rotation="vertical", fontsize=8)
ax.set_yscale("log")
ax.grid()

plt.tight_layout(rect=(0.05, 0.05, 0.95, 0.95))

plt.savefig("gpu_timers.png")
print("saved gpu_timers.png")

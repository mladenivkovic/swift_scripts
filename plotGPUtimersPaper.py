#!/usr/bin/env python3

from swift_hardcoded_data import timer_names

import matplotlib

#  matplotlib.use("Agg")

import argparse
import os
import numpy as np
from matplotlib import pyplot as plt


# Assumed directory structure:
#  `node_dir/experiment_dir`
# for all node_dir in node_dirs and for all
# experiment_dir in experiment_dirs

node_dirs = ["gn001", "gn002"]
experiment_dirs = ["eagle12", "gresho256"]
timer_file = "timers_0.txt"


parser = argparse.ArgumentParser(
    prog="plotGPUtimersPaper.py",
    description="""
    plot the outputs of the timers for a paper.
    Names of node directories and experiment directory names are hardcoded in
    this script.
    """,
    epilog="""
    To get timers output with swift, first configure with
    `./configure --enable-timers` and then run swift with `./swift --timers`
    """,
)

parser.add_argument(
    "-z",
    "--include-step-zero",
    action="store_true",
    help="Include the zeroth step in the timing averages",
)


args = parser.parse_args()

# Which data do we include in the averages?
first_index = 1
if args.include_step_zero:
    first_index = 0






# Make plot

fig = plt.figure(figsize=(15, 5), dpi=200)
ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132)
ax3 = fig.add_subplot(133)

nbars = len(node_dirs) + len(experiment_dirs)

x = np.arange(3)
width = 1. / (nbars + 1)


def plot_bars(ax, pack_timer, launch_timer, unpack_timer, title):
    """
    Plots the data of a single task type onto an axis.

    Parameters
    ----------

    ax: axis object to plot onto
    pack_timer: string of timer name for packing timer
    launch_timer: string of timer name for launch timer
    unpack_timer: string of timer name for unpacking timer
    title: title to add to the axis
    """

    index = 0
    for node in node_dirs:
        for experiment in experiment_dirs:

            fullfile = os.path.join(node, experiment, timer_file)

            # Load data
            cols_to_use = []
            # add + 1: timer 0 is "step"
            cols_to_use.append(timer_names.index(pack_timer) + 1)
            cols_to_use.append(timer_names.index(launch_timer) + 1)
            cols_to_use.append(timer_names.index(unpack_timer) + 1)
            data = np.loadtxt(fullfile, usecols=cols_to_use)

            pack = data[first_index:, 0].sum()
            launch = data[first_index:, 1].sum()
            unpack = data[first_index:, 2].sum()

            total = pack + launch + unpack

            color = "C" + str(index)
            offset = index * width
            label =  node + "/" + experiment
            pltkwargs = {
                    "color": color,
                    "width": width,
                    }

            ax.bar(x[0] + offset, pack / total, **pltkwargs, label=label)
            ax.bar(x[1] + offset, launch / total, **pltkwargs)
            ax.bar(x[2] + offset, unpack / total, **pltkwargs)

            index += 1

    ax.set_title(title)

    return


plot_bars(ax1, "gpu_pack_density", "gpu_launch_density", "gpu_unpack_density", "Density")
plot_bars(ax2, "gpu_pack_gradient", "gpu_launch_gradient", "gpu_unpack_gradient", "Gradient")
plot_bars(ax3, "gpu_pack_force", "gpu_launch_force", "gpu_unpack_force", "Force")


# bar/ticks are centered on bar at location of x, so it starts already
# shifted by width/2.
xticks = x + 0.5 * (nbars - 1) * width
for ax in fig.axes:
    ax.set_xticks(xticks, ["pack", "launch", "unpack"])
    ax.legend()
    ax.grid()
ax1.set_ylabel("Fraction of total time for offload")



plt.tight_layout() #rect=(0.05, 0.05, 0.95, 0.95))

#  plt.show()
plt.savefig("gpu_timers_paper.pdf")
print("saved gpu_timers_paper.pdf")

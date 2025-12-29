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

# ------------------------------------------------------


# Plot parameters
params = {
    "axes.labelsize": 14,
    "axes.titlesize": 18,
    "font.size": 16,
    "font.family": "serif",
    "legend.fontsize": 12,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.major.width": 1.5,
    "ytick.major.width": 1.5,
    "axes.linewidth": 1.5,
    "text.usetex": True,
    #  "figure.subplot.left": 0.045,
    #  "figure.subplot.right": 0.99,
    #  "figure.subplot.bottom": 0.05,
    #  "figure.subplot.top": 0.99,
    "figure.subplot.wspace": 0.,
    #  "figure.subplot.hspace": 0.12,
}
matplotlib.rcParams.update(params)




parser = argparse.ArgumentParser(
    prog="plotGPUtimersPaper.py",
    description="""
    plot the outputs of the timers for a paper.
    Names of node directories and experiment directory names are hardcoded in
    this script.
    By default, it makes 3 plots: One for each task subtype.
    Use -o to plot for each operation (pack, unpack, launch) per plot instead.
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

parser.add_argument(
    "-o",
    "--by-operation",
    action="store_true",
    help="Plot times by operation, not by task subtype",
)



args = parser.parse_args()

# Which data do we include in the averages?
first_index = 1
if args.include_step_zero:
    first_index = 0

by_operation = args.by_operation


# Read in data

results = {}

for node in node_dirs:

    results[node] = {}

    for experiment in experiment_dirs:

        fullfile = os.path.join(node, experiment, timer_file)

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

        data = np.loadtxt(fullfile, usecols=cols_to_use)

        density = {
                "pack": data[first_index:, 0].sum(),
                "unpack": data[first_index:, 3].sum(),
                "launch": data[first_index:, 6].sum(),
                }
        gradient = {
                "pack": data[first_index:, 1].sum(),
                "unpack": data[first_index:, 4].sum(),
                "launch": data[first_index:, 7].sum(),
                }
        force = {
                "pack": data[first_index:, 2].sum(),
                "unpack": data[first_index:, 5].sum(),
                "launch": data[first_index:, 8].sum(),
                }

        density["total"] = density["pack"] + density["unpack"] + density["launch"]
        gradient["total"] = gradient["pack"] + gradient["unpack"] + gradient["launch"]
        force["total"] = force["pack"] + force["unpack"] + force["launch"]


        experiment_result = {
                "density": density,
                "gradient": gradient,
                "force": force
                }

        results[node][experiment] = experiment_result




# Make plot

fig = plt.figure(figsize=(14, 4), dpi=200)
ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132, sharey=ax1)
ax3 = fig.add_subplot(133, sharey=ax1)



nbars = len(node_dirs) + len(experiment_dirs)

x = np.arange(3)
width = 1. / (nbars + 1)

# bar/ticks are centered on bar at location of x, so it starts already
# shifted by width/2.
xticks = x + 0.5 * (nbars - 1) * width

hatches = ['\\\\\\\\\\\\', "//////", "||", "--", ]

def plot_by_task_subtype(ax, task_type, title):
    """
    Plots the data of a single task (sub)type onto an axis.

    Parameters
    ----------

    ax: axis object to plot onto
    task_type: task type (density, force, gradient) to plot
    title: title to add to the axis
    """

    index = 0
    for n, node in enumerate(node_dirs):
        for e, experiment in enumerate(experiment_dirs):

            pack = results[node][experiment][task_type]["pack"]
            unpack = results[node][experiment][task_type]["unpack"]
            launch = results[node][experiment][task_type]["launch"]
            total = results[node][experiment][task_type]["total"]

            color = "C" + str(n)
            offset = index * width
            label =  node + "/" + experiment
            hatch = hatches[e]
            pltkwargs = {
                    "color": color,
                    "edgecolor": color,
                    "width": width,
                    "hatch": hatch,
                    "fill": False,
                    }

            ax.bar(x[0] + offset, pack / total, **pltkwargs, label=label)
            ax.bar(x[1] + offset, launch / total, **pltkwargs)
            ax.bar(x[2] + offset, unpack / total, **pltkwargs)

            index += 1

    ax.set_title(title)
    ax.set_xticks(xticks, ["pack", "launch", "unpack"])

    return



def plot_by_operation(ax, operation, title):
    """
    Plots the data of a single operation onto an axis.

    Parameters
    ----------

    ax: axis object to plot onto
    operation: string of operation name (pack, unpack, launch) for packing
    timer
    title: title to add to the axis
    """

    index = 0
    for n, node in enumerate(node_dirs):
        for e, experiment in enumerate(experiment_dirs):

            density = results[node][experiment]["density"][operation]
            gradient = results[node][experiment]["gradient"][operation]
            force = results[node][experiment]["force"][operation]

            total_density = results[node][experiment]["density"]["total"]
            total_gradient = results[node][experiment]["gradient"]["total"]
            total_force = results[node][experiment]["force"]["total"]

            color = "C" + str(n)
            offset = index * width
            label =  node + "/" + experiment
            hatch = hatches[e]
            pltkwargs = {
                    "color": color,
                    "edgecolor": color,
                    "width": width,
                    "hatch": hatch,
                    "fill": False,
                    }

            ax.bar(x[0] + offset, density / total_density, **pltkwargs, label=label)
            ax.bar(x[1] + offset, gradient / total_gradient, **pltkwargs)
            ax.bar(x[2] + offset, force / total_force, **pltkwargs)

            index += 1


    ax.set_title(title)
    ax.set_xticks(xticks, ["density", "gradient", "force"])
    ax.set_ylim([0, 1.0])

    return





if by_operation:
    plot_by_operation(ax1, "pack", "Pack")
    plot_by_operation(ax2, "launch", "Launch")
    plot_by_operation(ax3, "unpack", "Unpack")



else:
    plot_by_task_subtype(ax1, "density", "Density")
    plot_by_task_subtype(ax2, "gradient", "Gradient")
    plot_by_task_subtype(ax3, "force", "Force")


for ax in fig.axes:
    #  ax.legend()
    ax.grid(axis="y")

ax1.set_ylabel("Fraction of total time (per interaction loop)")
ax3.legend()
#  ax2.set_yticklabels([])
#  ax3.set_yticklabels([])



plt.tight_layout() #rect=(0.05, 0.05, 0.95, 0.95))

#  plt.show()
figname="gpu_timers_paper.pdf"
if by_operation:
    figname="gpu_timers_paper_by_operation.pdf"

#  plt.show()
plt.savefig(figname)
print(figname)


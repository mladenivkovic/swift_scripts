#!/usr/bin/env python3

# =====================================
# a quick plot for swift outputs
# =====================================


import numpy as np
import matplotlib.pyplot as plt

#  from matplotlib import colors as mcolors

import subprocess
import argparse

from swiftsimio import load


# Plot parameters
params = {
    "axes.labelsize": 10,
    "axes.titlesize": 12,
    "font.size": 10,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "text.usetex": True,
    "figure.subplot.left": 0.09,
    "figure.subplot.right": 0.93,
    "figure.subplot.bottom": 0.08,
    "figure.subplot.top": 0.96,
    "figure.subplot.wspace": 0.15,
    "figure.subplot.hspace": 0.12,
    "lines.markersize": 1,
    "lines.markeredgewidth": 0,
    "font.family": "sans-serif",
}
plt.rcParams.update(params)


def getargs():
    """
    Read cmd line args.
    """

    parser = argparse.ArgumentParser(
        description="""
        A program to quickly plot swift outputs.
        Will plot position scatter plot along z axis.
        """
    )

    #  parser.add_help(True)
    parser.add_argument("filename", help="IC or output file name to plot")
    parser.add_argument(
        "-l",
        "--legend",
        required=False,
        dest="legend",
        action="store_const",
        const=True,
        default=False,
        help="Add a legend to the plot",
    )

    args = parser.parse_args()

    infile = args.filename
    draw_legend = args.legend

    return infile, draw_legend


def main():

    infile, draw_legend = getargs()

    data = load(infile)
    meta = data.metadata
    boxsize = meta.boxsize

    # check for redshift and time. Might be missing
    # in some initial conditions.
    no_redshift = False
    no_time = False
    try:
        redshift = meta.redshift
    except AttributeError:
        no_redshift = True
    try:
        time = meta.t.in_units("Gyr")
    except AttributeError:
        no_time = True

    if draw_legend:
        figsize = (7, 6)
    else:
        figsize = (6, 6)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, aspect="equal")

    PPN = meta.present_particle_names
    handles = []
    if "dark_matter" in PPN:
        h1 = ax.scatter(
            data.dark_matter.coordinates[:, 0],
            data.dark_matter.coordinates[:, 1],
            fc="red",
            label="DM",
            alpha=0.5,
        )
        handles.append(h1)
    if "gas" in PPN:
        h2 = ax.scatter(
            data.gas.coordinates[:, 0],
            data.gas.coordinates[:, 1],
            fc="blue",
            label="gas",
            alpha=0.5,
        )
        handles.append(h2)
    if "stars" in PPN:
        h3 = ax.scatter(
            data.stars.coordinates[:, 0],
            data.stars.coordinates[:, 1],
            fc="gold",
            label="stars",
            alpha=0.5,
        )
        handles.append(h3)

    if len(handles) == 0:
        raise ValueError("Nothing to plot? No stars, gas, or DM?")

    if draw_legend:
        fig.legend(handles=handles, loc="upper right")

    title = r"\verb|{}|".format(infile)
    if no_redshift and no_time:
        pass
    elif no_redshift:
        title += "; t= {1:.3e}".format(time)
    elif no_time:
        title += "; z = {0:.3f}".format(redshift)
    else:
        title += "; z = {0:.3f}, t= {1:.3e}".format(redshift, time)

    ax.set_title(title)
    ax.set_xlabel("x [{}]".format(boxsize.units))
    ax.set_ylabel("y [{}]".format(boxsize.units))

    ax.set_xlim(0.0, boxsize[0])
    ax.set_ylim(0.0, boxsize[1])

    #  plt.show()

    if infile[-5:] == ".hdf5":
        outfile = infile.replace(".hdf5", "")
    elif infile[-3:] == ".h5":
        outfile = infile.replace(".h5", "")
    outfile += "-scatter.png"

    plt.savefig(outfile, dpi=200)

    subprocess.run(["eog", outfile])


if __name__ == "__main__":
    main()

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

from swift_hardcoded_data import *

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
    Returns: Parsed boolean flags.
    """

    parser = argparse.ArgumentParser(description="""
        A program to quickly plot swift outputs.
        Will plot particle position scatter plot along z axis.
        By default plots all available particles, unless overridden by using
        specific particle type flags (--dm, --hydro, --stars...)
        """)

    parser.add_argument("filename", help="IC or output file name to plot")
    parser.add_argument(
            "-g",
            "--dm",
            "--dark-matter",
            "--gravity",
            dest="plot_dm",
            action="store_true",
            default=False,
            help="Plot dark matter particle positions"
            )
    parser.add_argument(
            "-s",
            "--stars",
            dest="plot_stars",
            action="store_true",
            default=False,
            help="Plot star particle positions"
            )
    parser.add_argument(
            "-H",
            "--hydro",
            dest="plot_hydro",
            action="store_true",
            default=False,
            help="Plot hydro particle positions"
            )
    parser.add_argument(
        "-l",
        "--legend",
        required=False,
        dest="legend",
        action="store_true",
        default=False,
        help="Add a legend to the plot",
    )
    parser.add_argument(
        "-p",
        "--plain",
        "--no-labels",
        required=False,
        dest="plain",
        action="store_true",
        default=False,
        help="Don't add title and axis labels to plot",
    )
    parser.add_argument(
        "-c",
        "--color",
        "--colour",
        required=False,
        dest="colour",
        action="store_true",
        default=False,
        help="Colour in the particles by type",
    )
    parser.add_argument(
        "-d",
        "--dots",
        required=False,
        dest="dots",
        action="store_true",
        default=False,
        help="Use dots instead of (small) circles for particles",
    )


    args = parser.parse_args()

    infile = args.filename
    draw_legend = args.legend
    plot_hydro = args.plot_hydro
    plot_dm = args.plot_dm
    plot_stars = args.plot_stars
    plain = args.plain
    colour = args.colour
    dots = args.dots

    return infile, draw_legend, plot_hydro, plot_dm, plot_stars, plain, colour, dots


def main():

    infile, draw_legend, plot_hydro, plot_dm, plot_stars, plain, use_colour, dots = getargs()
    plot_all = (not plot_hydro) and (not plot_dm) and (not plot_stars)

    data = load(infile)
    meta = data.metadata
    boxsize = meta.boxsize
    available_types = meta.header["CanHaveTypes"]

    scatter_kwargs = {"alpha": 0.5}

    colours = {"dm": "k", "hydro": "k", "stars":"k"}
    if use_colour or draw_legend:
        colours = {"dm": "red", "hydro": "blue", "stars":"gold"}



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

    handles = []

    if plot_dm or plot_all:
        if available_types[SWIFT_TYPE_DARK_MATTER]:
            h1 = ax.scatter(
                data.dark_matter.coordinates[:, 0],
                data.dark_matter.coordinates[:, 1],
                fc=colours["dm"],
                label="DM",
                alpha=0.5,
            )
            handles.append(h1)
        else:
            if plot_dm:
                print(f"Error: DM particles not found in {infile}")
                quit(1)


    if plot_hydro or plot_all:
        if available_types[SWIFT_TYPE_GAS]:
            h2 = ax.scatter(
                data.gas.coordinates[:, 0],
                data.gas.coordinates[:, 1],
                fc=colours["hydro"],
                label="gas",
                alpha=0.5,
            )
            handles.append(h2)
        else:
            if plot_hydro:
                print(f"Error: Hydro particles not found in {infile}")
                quit(1)

    if plot_stars or plot_all:
        if available_types[SWIFT_TYPE_STARS]:
            h3 = ax.scatter(
                data.stars.coordinates[:, 0],
                data.stars.coordinates[:, 1],
                fc=colours["stars"],
                label="stars",
                alpha=0.5,
            )
            handles.append(h3)
        else:
            if plot_stars:
                print(f"Error: Star particles not found in {infile}")
                quit(1)

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

    if plain:
        ax.set_xticklabels([])
        ax.set_xticks([])
        ax.set_yticklabels([])
        ax.set_yticks([])
    else:
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

    plt.tight_layout()

    plt.savefig(outfile, dpi=200)

    subprocess.run(["eog", outfile])


if __name__ == "__main__":
    main()

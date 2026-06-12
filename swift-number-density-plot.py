#!/usr/bin/env python3

# =====================================
# plots projection of number density
# =====================================


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

import subprocess
import argparse

from swiftsimio import load
from swiftsimio.visualisation.projection import project_gas

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
        A program to quickly plot particle number densities of swift outputs.
        """)

    parser.add_argument("filename", help="IC or output file name to plot")
    #  parser.add_argument(
    #          "-g",
    #          "--dm",
    #          "--dark-matter",
    #          "--gravity",
    #          dest="plot_dm",
    #          action="store_true",
    #          default=False,
    #          help="Plot dark matter particle positions"
    #          )
    #  parser.add_argument(
    #          "-s",
    #          "--stars",
    #          dest="plot_stars",
    #          action="store_true",
    #          default=False,
    #          help="Plot star particle positions"
    #          )
    #  parser.add_argument(
    #          "-H",
    #          "--hydro",
    #          dest="plot_hydro",
    #          action="store_true",
    #          default=False,
    #          help="Plot hydro particle positions"
    #          )
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
        "-n",
        "--nx",
        required=False,
        dest="nx",
        default=1024,
        type=int,
        help="Pixel size for the plot",
    )


    args = parser.parse_args()

    infile = args.filename
    #  plot_hydro = args.plot_hydro
    #  plot_dm = args.plot_dm
    #  plot_stars = args.plot_stars
    plot_hydro = True
    plot_dm = False
    plot_stars = False
    plain = args.plain
    nx = args.nx

    return infile, plot_hydro, plot_dm, plot_stars, plain, nx


def main():

    infile, plot_hydro, plot_dm, plot_stars, plain, nx = getargs()
    plot_all = (not plot_hydro) and (not plot_dm) and (not plot_stars)
    if plot_all:
        raise NotImplementedError()

    data = load(infile)
    meta = data.metadata
    boxsize = meta.boxsize
    available_types = meta.header["CanHaveTypes"]


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

    figsize = (6.5, 6)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, aspect="equal")

    if plot_dm or plot_all:
        raise NotImplementedError()
        #  if available_types[SWIFT_TYPE_DARK_MATTER]:
        #  else:
        #      if plot_dm:
        #          print(f"Error: DM particles not found in {infile}")
        #          quit(1)



    if plot_hydro or plot_all:
        if available_types[SWIFT_TYPE_GAS]:

            mass_map = project_gas(data, nx, project="masses", parallel=True)
            #  density_map = project_gas(data, nx, project="densities", parallel=True)
            #  number_density_map = density_map / mass_map
            #  mean_mass = np.mean(data.gas.masses)
            # seems to struggle with np.mean()...
            mean_mass = data.gas.masses.sum() / len(data.gas.masses)
            number_density_map = mass_map / mean_mass

            im = ax.imshow(
                number_density_map.value.T,
                origin="lower",
                cmap="YlGnBu_r",
                extent=(0, boxsize.value[0], 0, boxsize.value[1]),
                norm=mcolors.SymLogNorm(1e-6),
                )

            cb = fig.colorbar(im, fraction=0.046, pad=0.01)
            cb.ax.set_ylabel("$" + number_density_map.units.latex_repr + "$")

        else:
            if plot_hydro:
                print(f"Error: Hydro particles not found in {infile}")
                quit(1)

    if plot_stars or plot_all:
        raise NotImplementedError()
        #  if available_types[SWIFT_TYPE_STARS]:
        #  else:
        #      if plot_stars:
        #          print(f"Error: Star particles not found in {infile}")
        #          quit(1)


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
        ax.set_xlabel("[{}]".format(boxsize.units))
        ax.set_ylabel("[{}]".format(boxsize.units))
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
    outfile += "-number-density.png"

    plt.tight_layout()

    plt.savefig(outfile, dpi=200)
    print(f"Saved {outfile}")

    #  subprocess.run(["eog", outfile])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# =====================================
# a quick plot for swift outputs
# =====================================


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

import subprocess
import argparse

from swiftsimio import load
from swiftsimio.visualisation.projection import project_gas


infile = None

names = {}
# dict of plotting cases -> array names
names["mass"] = "masses"
names["density"] = "densities"
names["h"] = "smoothing_lengths"
names["internal energy"] = "internal_energies"
names["entropy"] = "entropies"

nx_default = 1024


# Plot parameters
params = {
    "axes.labelsize": 10,
    "axes.titlesize": 12,
    "font.size": 10,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "text.usetex": True,
    "figure.subplot.left": 0.02,
    "figure.subplot.right": 0.91,
    "figure.subplot.bottom": 0.08,
    "figure.subplot.top": 0.96,
    "figure.subplot.wspace": 0.15,
    "figure.subplot.hspace": 0.12,
    "lines.markersize": 6,
    "lines.linewidth": 3.0,
    #  'text.latex.unicode': False
}
plt.rcParams.update(params)
plt.rc("font", **{"family": "sans-serif", "sans-serif": ["Times"]})


def getargs():
    """
    Read cmd line args.
    """

    parser = argparse.ArgumentParser(
        description="""
        A program to quickly plot swift outputs.
        Will plot mass projection along z axis as default.
        """
    )

    #  parser.add_help(True)
    parser.add_argument("filename")
    parser.add_argument(
        "--mass",
        dest="to_plot",
        action="store_const",
        const="mass",
        default="mass",
        help="project mass",
    )
    parser.add_argument(
        "--sl",
        dest="to_plot",
        action="store_const",
        const="h",
        default="mass",
        help="project smoothing length",
    )
    parser.add_argument(
        "--dens",
        dest="to_plot",
        action="store_const",
        const="density",
        default="mass",
        help="project mass density",
    )
    parser.add_argument(
        "--rho",
        dest="to_plot",
        action="store_const",
        const="density",
        default="mass",
        help="project mass density",
    )
    parser.add_argument(
        "--u",
        dest="to_plot",
        action="store_const",
        const="internal energy",
        default="mass",
        help="project internal energy",
    )
    parser.add_argument(
        "--ent",
        dest="to_plot",
        action="store_const",
        const="entropy",
        default="mass",
        help="project entropy",
    )
    #  parser.add_argument('--pt',
    #          dest='ptype',
    #          action='store',
    #          default='PartType0',
    #          help='PartType to use. Default=PartType0')
    #  parser.add_argument('--dm',
    #          dest='ptype',
    #          action='store_const',
    #          const='PartType1',
    #          help='use dark matter particle type (PartType1)')
    parser.add_argument(
        "--nx",
        dest="nx",
        type=int,
        action="store",
        default=nx_default,
        help="Image pixel resolution.",
    )

    args = parser.parse_args()

    infile = args.filename
    to_plot = args.to_plot
    nx = args.nx

    return infile, to_plot, nx


def main():

    infile, to_plot, nx = getargs()

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

    mymap = project_gas(data, resolution=nx, project=names[to_plot], parallel=True)

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, aspect="equal")

    im = ax.imshow(
        mymap.value.T,
        origin="lower",
        cmap="YlGnBu_r",
        extent=(0, boxsize.value[0], 0, boxsize.value[1]),
        norm=mcolors.SymLogNorm(1e-6),
    )

    cb = fig.colorbar(im, fraction=0.046, pad=0.01)
    cb.ax.set_ylabel(to_plot + " [$" + mymap.units.latex_repr + "$]")

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

    if infile[-5:] == ".hdf5":
        outfile = infile.replace(".hdf5", "")
    elif infile[-3:] == ".h5":
        outfile = infile.replace(".h5", "")
    outfile += "-{}.png".format(names[to_plot])

    plt.savefig(outfile, dpi=200)

    subprocess.run(["eog", outfile])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# =====================================
# Print out particle data for a swift
# hdf5 file.
# usage:
#   swift-printparticles.py <fname>
# =====================================


import numpy as np
import argparse
import h5py


errormsg = """
I need a file as a cmd line arg to print it.
Usage:
    swift-printparticles.py <fname>
"""


tosort = None
sort_by = None
for_debug = False
debugtools = None


def getargs():

    """
    Read cmd line args.
    """

    import sys
    import os

    parser = argparse.ArgumentParser(
        description="""
        A program to print particle data.
            """
    )

    parser.add_argument("filename")
    parser.add_argument(
        "--pt",
        dest="ptype",
        action="store",
        default="PartType0",
        help="PartType to use. Default=PartType0",
    )
    parser.add_argument(
        "-s",
        dest="tosort",
        action="store_const",
        const="ids",
        help="Flag to sort particles by ID",
    )
    parser.add_argument(
        "--sort-id",
        dest="sort_by",
        action="store_const",
        const="ids",
        help="Flag to sort particles by ID",
    )
    parser.add_argument(
        "--grads",
        dest="debugtool",
        action="store_const",
        const="grads",
        help='Print the "GradientSum" field only with IDs',
    )

    args = parser.parse_args()

    global tosort, sort_by, for_debug, debugtools

    fname = args.filename
    tosort = args.tosort
    ptype = args.ptype

    try:
        fname = sys.argv[1]
        if not os.path.isfile(fname):
            print("Given filename, '", fname, "' is not a file.")
            print(errormsg)
            quit(2)
    except IndexError:
        print(errormsg)
        quit(2)

    if tosort:  # -s flag; set sort_by to ids
        sort_by = "ids"

    if args.sort_by is not None:
        tosort = True
        sort_by = args.sort_by

    if args.debugtool is not None:
        for_debug = True
        debugtools = args.debugtool

    return fname, ptype


def read_file(srcfile, ptype):
    """
    Read swift output hdf5 file.
    """

    import h5py

    f = h5py.File(srcfile)

    x = f[ptype]["Coordinates"][:, 0]
    y = f[ptype]["Coordinates"][:, 1]
    z = f[ptype]["Coordinates"][:, 2]
    m = f[ptype]["Masses"][:]
    ids = f[ptype]["ParticleIDs"][:]

    try:
        # old SWIFT header versions
        rho = f[ptype]["Density"][:]
    except KeyError:
        # new SWIFT header versions
        try:
            rho = f[ptype]["Densities"][:]
        except KeyError:
            print(
                "This file doesn't have a density dataset (Could be the case for IC files.). Skipping it."
            )
            rho = None

    try:
        # old SWIFT header versions
        h = f[ptype]["SmoothingLength"][:]
    except KeyError:
        # new SWIFT header versions
        h = f[ptype]["SmoothingLengths"][:]

    if for_debug:
        if debugtools == "grads":
            debug_array = f[ptype]["GradientSum"][:]
    else:
        debug_array = None

    f.close()

    return x, y, z, h, rho, m, ids, debug_array


def print_particles(x, y, z, h, rho, m, ids, debug_array):

    if tosort:
        if sort_by == "ids":
            inds = np.argsort(ids, axis=0)
    else:
        inds = range(x.shape[0])

    if for_debug:

        if debug_array is None:
            print("debug_array is None. Something went wrong.")
            quit(1)

        print("{0:6} | {1:12}".format("ID", "Debug array"))
        print(
            "-------------------------------------------------------------------------"
        )
        for i in inds:
            print("{0:6d} | ".format(ids[i]), end="")
            if debug_array.ndim == 1:
                print("{0:14} ".format(debug_array[i]))
            else:
                #  print(debug_array.dtype.name, type(debug_array.dtype))
                if "float" in debug_array.dtype.name:
                    for j in range(debug_array.ndim):
                        print("{0:14.8f} ".format(debug_array[i, j]), end="")
                else:
                    for j in range(debug_array.ndim):
                        print("{0:14d} ".format(debug_array[i, j]), end="")

                print("")

    else:

        if rho is not None:
            print(
                "{0:6} | {1:10} {2:10} {3:10} | {4:10} {5:10} {6:10} |".format(
                    "ID", "x", "y", "z", "h", "m", "rho"
                )
            )
            print(
                "------------------------------------------------------------------------------"
            )

            for i in inds:
                print(
                    "{0:6d} | {1:10.4f} {2:10.4f} {3:10.4f} | {4:10.4f} {5:10.4f} {6:10.4f} |".format(
                        ids[i], x[i], y[i], z[i], h[i], m[i], rho[i]
                    )
                )

        else:
            print(
                "{0:6} | {1:10} {2:10} {3:10} | {4:10} {5:10} |".format(
                    "ID", "x", "y", "z", "h", "m"
                )
            )
            print("-------------------------------------------------------------------")

            for i in inds:
                print(
                    "{0:6d} | {1:10.4f} {2:10.4f} {3:10.4f} | {4:10.4f} {5:10.4f} |".format(
                        np.asscalar(ids[i]),
                        np.asscalar(x[i]),
                        np.asscalar(y[i]),
                        np.asscalar(z[i]),
                        np.asscalar(h[i]),
                        np.asscalar(m[i]),
                    )
                )

    return


def main():

    fname, ptype = getargs()
    x, y, z, h, rho, m, ids, debug_array = read_file(fname, ptype)

    print_particles(x, y, z, h, rho, m, ids, debug_array)

    return


if __name__ == "__main__":
    main()

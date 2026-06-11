#!/usr/bin/env python3

# ============================================
# Print out boxsize for a swift hdf5 file.
# usage:
#   swift-boxsize.py <fname>
# ============================================


import numpy as np
import argparse
import h5py

errormsg = """
I need a file as a cmd line arg to print it.
Usage:
    swift-boxsize.py <fname>
"""


def getargs():
    """
    Read cmd line args.
    """

    import sys
    import os

    parser = argparse.ArgumentParser(description="""
        A program to print the boxsize of SWIFT output.
            """)

    parser.add_argument("filename")

    args = parser.parse_args()

    try:
        fname = sys.argv[1]
        if not os.path.isfile(fname):
            print("Given filename, '", fname, "' is not a file.")
            print(errormsg)
            quit(2)
    except IndexError:
        print(errormsg)
        quit(2)

    return fname


def read_file(srcfile):
    """
    Read swift output hdf5 file.
    """

    import h5py

    f = h5py.File(srcfile)

    h = f["Header"]

    boxsize = h.attrs["BoxSize"]

    u = f["Units"]
    unit = u.attrs["Unit length in cgs (U_L)"]

    f.close()

    return boxsize, unit


def main():

    fname = getargs()
    boxsize, unit = read_file(fname)

    pc = 3.0857e18 # parsec in cm

    print(f"Boxsize is ")
    print(f"        {boxsize} x {unit[0] :.3e} cm")
    print(f"        {boxsize} x {unit[0] / pc :.3e} pc")
    print(f"        {boxsize} x {unit[0] / (pc * 1e6):.3e} Mpc")

    return


if __name__ == "__main__":
    main()

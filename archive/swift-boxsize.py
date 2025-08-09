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

    parser = argparse.ArgumentParser(
        description="""
        A program to print particle data.
            """
    )

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

    f.close()

    return boxsize


def main():

    fname = getargs()
    boxsize = read_file(fname)

    print("Boxsize is:", boxsize)

    return


if __name__ == "__main__":
    main()

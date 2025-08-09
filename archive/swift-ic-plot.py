#!/usr/bin/env python3

import numpy as np
import unyt
from scipy.spatial import cKDTree
from swiftsimio import load
from swiftsimio.visualisation.projection import project_gas
from swiftsimio.initial_conditions.IC_kernel import get_kernel_data

import argparse
from os import path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors


# Plot parameters
params = {
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "font.size": 12,
    "legend.fontsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "text.usetex": True,
    "figure.subplot.left": 0.05,
    "figure.subplot.right": 0.99,
    "figure.subplot.bottom": 0.12,
    "figure.subplot.top": 0.99,
    "figure.subplot.wspace": 0.25,
    "figure.subplot.hspace": 0.20,
    "lines.markersize": 1,
    "lines.linewidth": 3.0,
    "text.latex.unicode": True,
}
matplotlib.rcParams.update(params)
matplotlib.rc("font", **{"family": "sans-serif", "sans-serif": ["Times"]})


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

    args = parser.parse_args()

    infile = args.filename

    if not path.exists(infile):
        raise ValueError("Given file doesn't exist.")

    return infile


def compute_approximate_density(data):
    """
    Compute approximate density if it is not present in 
    the IC file.
    """

    x = data.gas.coordinates
    m = data.gas.masses
    h = data.gas.smoothing_length

    npart = m.shape[0]
    ndim = data.metadata.dimension
    boxsize = data.metadata.boxsize

    rho = unyt.unyt_array(
        np.zeros(m.shape), m.units
    )  # change to density units after neighbour loop
    neighbours = min(50, npart)

    kernel_func, _, kernel_gamma = get_kernel_data("cubic spline", ndim)

    tree = cKDTree(x, boxsize=boxsize)
    for p in range(npart):
        dist, neighs = tree.query(
            x[p], distance_upper_bound=kernel_gamma * h[p], k=neighbours
        )
        # tree.query returns index nparts+1 if not enough neighbours were found
        mask = neighs < npart
        dist = dist[mask]
        neighs = neighs[mask]
        if neighs.shape[0] == 0:
            raise RuntimeError("Found no neighbour for a particle.")
        H = dist[-1]
        for i, n in enumerate(neighs):
            W = kernel_func(dist[i], H)
            rho[p] += W * m[n]

    rho = unyt.unyt_array(rho.value, m.units / x.units ** ndim)

    return rho


def plot_1D(data):
    """
    creates 1D plots.
    data: swift IC file data as returned from swiftsimio.load()
    """

    x = data.gas.coordinates
    m = data.gas.masses
    h = data.gas.smoothing_length
    try:
        rho = data.gas.density
    except AttributeError:
        rho = compute_approximate_density(data)

    u = data.gas.internal_energy
    v = data.gas.velocities

    fig = plt.figure(figsize=(12, 4))

    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)

    ax1.scatter(x[:, 0], rho)
    ax1.set_ylabel("density")
    ax1.set_xlabel("x")
    ax2.scatter(x[:, 0], v)
    ax2.set_ylabel("velocity")
    ax2.set_xlabel("x")
    ax3.scatter(x[:, 0], u)
    ax3.set_ylabel("internal energy")
    ax3.set_xlabel("x")

    return fig


def plot_2D(data):
    """
    creates 1D plots.
    data: swift IC file data as returned from swiftsimio.load()
    """

    boxsize = data.metadata.boxsize.value
    extent = (0, boxsize[0], 0, boxsize[1])

    resolution = min(100, int(np.sqrt(data.gas.masses.shape[0])) + 1)

    mass_map = project_gas(
        data, resolution=resolution, project="masses", parallel="True"
    )
    velocity_map = project_gas(
        data, resolution=resolution, project="velocities", parallel="True"
    )
    energy_map = project_gas(
        data, resolution=resolution, project="internal_energy", parallel="True"
    )

    plt.imsave("test.png", mass_map)

    fig = plt.figure(figsize=(12, 4))

    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)

    im1 = ax1.imshow(mass_map.value.T, extent=extent)
    fig.colorbar(im1, ax=ax1)
    ax1.set_title("density")

    im2 = ax2.imshow(velocity_map.value.T, extent=extent)
    fig.colorbar(im2, ax=ax2)
    ax2.set_title("velocity")

    im3 = ax3.imshow(energy_map.value.T, extent=extent)
    fig.colorbar(im3, ax=ax3)
    ax3.set_title("internal energy")

    return fig


if __name__ == "__main__":
    infile = getargs()

    data = load(infile)
    meta = data.metadata
    if meta.dimension == 1:
        fig = plot_1D(data)
    elif meta.dimension == 2:
        fig = plot_2D(data)

    figname, h5 = path.splitext(infile)
    plt.savefig(figname + ".png", dpi=200)

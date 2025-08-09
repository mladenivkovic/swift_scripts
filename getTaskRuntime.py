#!/usr/bin/env python3

import argparse
import os
import numpy as np
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(
    prog="getTaskRuntime.py",
    description="Collect the runtimes of the tasks",
)

parser.add_argument(
    "timesteps_file",
    nargs="?",
    action="store",
    default="timers_0.txt",
    help="file to read in. Default: 'timesteps.txt'",
    type=str,
)
parser.add_argument(
    "-s", "--skip-step-zero", action="store_true", help="skip the zeroth step"
)
args = parser.parse_args()

if not os.path.exists(args.timesteps_file):
    print(f"Couldn't find timer file {args.timesteps_file}.")
    exit(1)


data = np.loadtxt(args.timesteps_file, usecols=[12, 14])
if args.skip_step_zero:
    print("Skipping zeroth step")
    data = data[1:]

time_total = data[:, 0].sum()
time_avg = data[:, 0].mean()
time_min = data[:, 0].min()
time_max = data[:, 0].max()

deadtime_total = data[:, 1].sum()
deadtime_avg = data[:, 1].mean()
deadtime_min = data[:, 1].min()
deadtime_max = data[:, 1].max()

print("Time [s]:")
print(f"  Total: {time_total *1e-3:12.3f}")
print(f"  Avg:   {time_avg *1e-3:12.3f}")
print(f"  Min:   {time_min *1e-3:12.3f}")
print(f"  Max:   {time_max *1e-3:12.3f}")
print("Deadtime [s]:")
print(f"  Total: {deadtime_total *1e-3:12.3f}")
print(f"  Avg:   {deadtime_avg *1e-3:12.3f}")
print(f"  Min:   {deadtime_min *1e-3:12.3f}")
print(f"  Max:   {deadtime_max *1e-3:12.3f}")

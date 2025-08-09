#!/bin/bash

#--------------------------------------
# create the task plots for all
# thread_info-step*.dat files present
# in the current directory
#--------------------------------------

for threadfile in thread_info-step*.dat; do
    pngfile=${threadfile#thread_info-step}
    pngfile=${pngfile%.dat}
    python3 $HOME/local/swiftsim/tools/task_plots/plot_tasks.py $threadfile $pngfile
done

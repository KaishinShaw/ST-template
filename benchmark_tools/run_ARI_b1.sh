#!/bin/bash

# Check if model name is provided as a command-line argument
if [ -z "$1" ]; then
    echo "Usage: $0 model_name"
    exit 1
fi

model_name="$1"

# Define the array of dataset IDs
ids=('151507' '151508' '151509' '151510' '151669' '151670'
     '151671' '151672' '151673' '151674' '151675' '151676')

# Base directory for storing results
base_dir=~/"$model_name"/test_results

# Check if the log directory exists, if so, remove it
if [ -d "$base_dir"/log ]; then
    rm -rf "$base_dir"/log
fi

# Ensure the log directory exists
mkdir -p "$base_dir"/log

# Setup a global trap to ensure the GPU monitoring process is killed if the script exits prematurely
trap '[[ -n $monitor_pid ]] && kill $monitor_pid 2>/dev/null' EXIT

# Loop through each ID and execute the Python script
for id in "${ids[@]}"; do
    # Determine the number of clusters based on the dataset ID
    if [[ " ${ids[@]:4:4} " =~ " $id " ]]; then
        n_clusters=5
    else
        n_clusters=7
    fi

    # Start monitoring GPU memory usage in the background
    while true; do
        nvidia-smi --query-gpu=memory.used --format=csv >> "$base_dir"/log/memory_usage_"$id".csv
        sleep 1
    done &
    monitor_pid=$!

    # Execute the Python script and record the time
    /usr/bin/time -v python "${model_name}_ARI_test.py" $id $n_clusters > "$base_dir"/log/output_"${model_name}"${id} 2> "$base_dir"/log/time_log_"${model_name}"${id}
    
    # Kill the GPU monitoring process after the script finishes
    kill $monitor_pid
    monitor_pid=  # Clear PID after killing

    # Wait a moment to make sure the GPU monitoring has fully stopped
    sleep 2
done

# Clear the global trap
trap - EXIT
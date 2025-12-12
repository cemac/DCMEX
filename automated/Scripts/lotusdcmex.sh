#!/bin/bash
#SBATCH --job-name=dcmex0731
#SBATCH --partition=standard
#SBATCH --qos=high
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=3
#SBATCH --mem=16G
#SBATCH --account=dcmex
#SBATCH --output=logs/%x_%A_%a.out
#SBATCH --error=logs/%x_%A_%a.err

conda activate DCMEX

# Define the list of date strings (space-separated)
dates=("2022-07-31")

# Loop over each date
for date in "${dates[@]}"; do
  # Loop over both cameras
  for camera in 2; do
    echo "Processing $date for $camera"
    echo 'Creating optical depth plots and distance csv'
    #python optical_depth_plotter_interp16.py $camera $date
    echo 'Finding the cloud edges in photos and creating pixel csv'
    #python cloudtop_pixel_heights.py $camera $date
    echo 'Calulating cloud top heights and creating timeseries csv'
    #python calculate_heights.py $camera $date
    echo 'Creating image pairs of boxed clouds and optical depth'
    python image_pairs.py $camera $date
  done
done

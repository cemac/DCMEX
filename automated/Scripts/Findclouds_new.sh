#!/usr/bin/bash

conda activate DCMEX
camera=1
date='2022-07-31'
echo 'Creating optical depth plots and distance csv'
python optical_depth_plotter_interp16.py $camera $date
echo 'Finding the cloud edges in photos and creating pixel csv'
python cloudtop_pixel_heights.py $camera $date
echo 'Calulating cloud top heights and creating timeseries csv'
python calculate_heights.py $camera $date
echo 'Creating image pairs of boxed clouds and optical depth'
python image_pairs.py $camera $date

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optical Depth Plotter

Filter out cirrus cloud below 3.6
Plot camera FOV, orography and find location on max optical depth in that area

To run: 
python optical_depth_plotter.py <camera> <yyyy-mm-dd>
where:
    <camera> is an integer: 1/2
    <yyyy-mm-dd> is a date string e.g. <2022-07-29>

 
"""

# Load modules
import glob
import os
import pandas as pd
import sys
sys.path.append(os.path.abspath("/gws/nopw/j04/dcmex/users/hburns/DCMEX/StandAloneTools/"))
import Distance_Estimator as de

# Extract arguments
camera = int(sys.argv[1])
date_to_use = str(sys.argv[2])
# Path to area to write images and results to
storage = '/gws/nopw/j04/dcmex/users/hburns/'
# Path to write created images
imgroot = str(storage + "images2/FOV_on_optical_depth/" +
              date_to_use+'/camera/'+str(camera)+'/')
# Path to optical depth data
dataroot = '/gws/nopw/j04/dcmex/data'

# YAW Error (our measured YAW's don't look too acurate )
yaw_error = 10

# Optical depth threshold (cumulus cloud not cirrus)
optical_depth_threshold = 3.6

# Retireve camera details for the selected day
cam_details = storage + '/camera_details.csv'
cam_df = pd.read_csv(cam_details)

# -------- Extract relevant files and camera info --------------------------- #
# Create any folders that don't already exist
if not os.path.exists(imgroot):
    # If it doesn't exist, create it
    os.makedirs(imgroot)

if not os.path.exists(storage+'results2/'+date_to_use+'/'):
    os.makedirs(storage+'results2/'+date_to_use+'/')

# Select file names based on camera and date
if camera == 2:
    fnames = glob.glob(dataroot + '/stereocams/' + date_to_use +
                       '/secondary_red/amof-cam-2-' + date_to_use + '-*.jpg')
else:
    fnames = glob.glob(dataroot + '/stereocams/' + date_to_use +
                       '/primary_blue/amof-cam-1-' + date_to_use + '-*.jpg')
    
distances = []
datetimes = []
CT_lat = []
CT_lon = []
for fname in fnames:
    processor = de.CloudOpticalDepthProcessor(fname)
    D, maxlat_2, maxlon_2 = processor.process_file(show='save')
    # Append results to lists
    distances.append(D)
    datetimes.append(data[0].t[i].data)
    CT_lat.append(maxlat_2)
    CT_lon.append(maxlon_2)
# Create a DataFrame from the collected results and save it to a CSV file
cloud_distances = pd.DataFrame(
    {'Datetimes': datetimes, 'Distance': distances, 'CT_lat': CT_lat,
     'CT_lon': CT_lon})
cloud_distances.to_csv(
    storage + 'results2/' + date_to_use + '/Cloud_distnaces_camera_'
    + str(camera) + '.csv')

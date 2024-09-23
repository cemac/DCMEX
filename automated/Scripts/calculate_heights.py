#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
python script calculate_heights.py

author: helen burns CEMAC UoL 2023
python: 3.8 Jasmin NERC servers
project: DCMEX

Description

Usage: python     calculate_heights.py <camera> <date>
where
camera : interger 1 or 2
date : string 'yyyy-mm-dd'

this script takes the information generated in cloudtop_pixel_heights.py and 
optical_depth_plotter.py and calculates the cloud top height using the distance
to the cloud and the pixel location of cloud in each photo. This is done using
the thin lens equations 

The output of these scripts is csv file of time series of cloud heights and 
scatter plots of cloud top heights vs time. for completeness the cloud base
and x loc is also stored

"""
# Import modules
import sys
import math
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter


# Extract arguments
camera = int(sys.argv[1])
date_to_use = str(sys.argv[2])

# Processing date format
parts = date_to_use.split('-')
date = parts[-1]+'-'+parts[1]+'-'+parts[0]

# File storage path
storage = '/home/users/hburns/GWS/DCMEX/users/hburns/'

# Camera info
# https://www.digicamdb.com/specs/canon_eos-6d-mark-ii/
#
# 26,200,000 photosites (pixels) on this area. distance between pixels: 5.73 µm
# 861.6 mm2
#
# Sensor height = 35.9 x 24 mm so 24mm high
# Image width x height: 6240 x 4160
# Camera parameters
D = 1000        # Distance from camera to object in meters
focal_length_mm = 50         # Focal Length in mm
sensor_height_mm = 24        # Sensor height in mm
sensor_width_mm = 35.9       # Sensor width in mm
focal_length_mm = 50.0       # Focal length in mm
FOV = 0         # Field of View (to be calculated later)

# Height = (Distance to Object x Object height on sensor) / Focal Length

"""
Fundamentals of Photonics, Bahaa E. A. Saleh and Malvin Carl Teich, 2007, 
FOV diagram
Introduction to Modern Optics, Author: Grant R. Fowles,
Dover Publications, 1989 - thin lens equations

"""

# Calculating FOV angles in degrees

# Calculate FOV angles in radians
fov_horizontal_rad = 2 * math.atan(sensor_width_mm / (2 * focal_length_mm))
fov_vertical_rad = 2 * math.atan(sensor_height_mm / (2 * focal_length_mm))

# Convert FOV angles to degrees
fov_horizontal_deg = math.degrees(fov_horizontal_rad)
fov_vertical_deg = math.degrees(fov_vertical_rad)
FOV = fov_vertical_deg

# Displaying FOV angles
print("FOV Horizontal Angle:", fov_horizontal_deg, "degrees")
print("FOV Vertical Angle:", fov_vertical_deg, "degrees")

# Reading camera details and cloud data
cam_details = storage+'/camera_details.csv'
cam_df = pd.read_csv(cam_details)

# Function to find height of an object given its pixel position on the sensor


def find_height(P, Distance, focal_length_mm, sensor_height_mm):
    """
    Calculate the height of an object given its pixel position on the sensor.

    Parameters:
    - P: Pixel position of the object on the sensor
    - Distance: Distance to the object in millimeters
    - focal_length_mm: Focal length of the camera lens in millimeters
    - sensor_height_mm: Height of the camera sensor in millimeters

    Returns:
    - Height of the object in kilometers (rounded to 2 decimal places)
    """
    OHS = find_OHS(P, sensor_height_mm)
    H = (Distance * 10**3 * OHS) / focal_length_mm
    return round(H / 10**3, 2)

# Object height on sensor =  (Sensor height (mm) × Object height (pixels))
#                                      / Sensor height (pixels)
# Sensor height (px) = Sensor height (mm) / distance between pixels
# sensor_height_pixels = 24*10**-3 / 5.73*10**-6
# sensor_height_pixels = 4188

# Function to calculate Object Height on Sensor


def find_OHS(P, sensor_height_mm):
    """
    Calculate the Object Height on Sensor.

    Parameters:
    - P: Pixel position of the object on the sensor
    - sensor_height_mm: Height of the camera sensor in millimeters

    Returns:
    - Object Height on Sensor
    """
    sensor_height_pixels = 4188
    OHS = sensor_height_mm * P / sensor_height_pixels
    return OHS


def pitch_correct(P, FieldOfView, h):
    """
    Correct the pitch of the camera based on angles and height.

    Parameters:
    - P: Pixel position of the object on the sensor
    - FieldOfView: Field of View of the camera in degrees
    - h: Height on the inclined plane

    Returns:
    - True height after pitch correction
    """
    # See diagram for agles a, b and c
    a = 90 - P - FieldOfView/2
    b = 180 - 90 - FieldOfView/2
    # image plane incline from vertical
    c = 180 - a - b
    # x is true height, h is height on incled place
    x = h * math.cos(c)
    return x


# Filtering camera details for the given date and camera
filtered_df = cam_df[(cam_df['Date'] == date) & (cam_df['camera'] == camera)]
yaw_degrees = filtered_df.yaw.values[0]
pitch = filtered_df.pitch.values[0]
camera_height = filtered_df.height.values[0]/1000
cloud_distances = pd.read_csv(storage + '/results/' + date_to_use +
                              '/Cloud_distnaces_camera_' + str(camera) +
                              '.csv')
cloud_pixels = pd.read_csv(storage + '/results/' + date_to_use +
                           '/cloud_pixels_camera_' + str(camera) + '.csv')

# Formatting date and time
date_format_distances = '%Y-%m-%dT%H:%M:%S'
date_format_pixels = '%Y-%m-%dT%H%M%S'
date_object_distances = datetime.strptime(
    cloud_distances.Datetimes.iloc[0].split('.')[0], date_format_distances)
date_object_pixels = datetime.strptime(
    date_to_use+'T'+str(cloud_pixels.Times.iloc[0]), date_format_pixels)

# Adding Date_Time columns to DataFrames
cloud_distances['Date_Time'] = pd.to_datetime(cloud_distances.Datetimes)
cloud_pixels['Date_Time'] = ''
for index, row in cloud_pixels.iterrows():
    cloud_pixels['Date_Time'].iloc[index] = datetime.strptime(
        date_to_use+'T'+str(cloud_pixels.Times.iloc[index]),
        date_format_pixels)

# Matching cloud distances to corresponding pixels
cloud_pixels['Distance'] = ''
for index, row in cloud_pixels.iterrows():
    timestamp1 = row.Date_Time

    # Iterate through files in folder2 to find the closest match
    closest_file2 = None
    closest_time_difference = float('inf')
    for index2, row2 in cloud_distances.iterrows():

        timestamp2 = row2.Date_Time
        time_difference = abs((timestamp1 - timestamp2).total_seconds())

        if time_difference < closest_time_difference:
            closest_time_difference = time_difference
            closest_file2 = row2

    # Load images and create a subplot
    if closest_file2 is not None:
        cloud_pixels['Distance'].iloc[index] = closest_file2.Distance


# Filtering cloud dataframe based on distance criteria
try:
    condition = (cloud_pixels['Distance'] > 30) | (
        cloud_pixels['Distance'] < 10)
except TypeError:
    cloud_pixels = cloud_pixels[cloud_pixels != 'no cloud']
    cloud_pixels['Distance'] = pd.to_numeric(cloud_pixels['Distance'])
    condition = (cloud_pixels['Distance'] > 30) | (
        cloud_pixels['Distance'] < 10)


df_filtered = cloud_pixels[~condition]
# Initializing DataFrame for processed data
df_filtered = df_filtered.reset_index(drop=True)
df2 = pd.DataFrame(index=range(len(df_filtered)), columns=[
                   'Time', 'distance_to_cloud', 'CT1', 'CT2', 'CB1', 'CB2',
                   'CTP1', 'CTP2', 'CBP1', 'CTBP2', 'W1', 'W2', 'X1', 'X2',
                   'MAXCTH'])

# Processing cloud data to calculate heights and distances
for row in df_filtered.itertuples():
    CT2 = row.CT1
    CT1 = row.CT2
    W1 = row.W1
    X1 = row.CX1
    CB1 = row.CB1
    W2 = row.W2
    X2 = row.CX2
    CB2 = row.CB2
    hb1 = find_height(4160-CT1, row.Distance,
                      focal_length_mm, sensor_height_mm)
    ht1 = find_height(4160-CB1, row.Distance,
                      focal_length_mm, sensor_height_mm)
    CTH1 = round(pitch_correct(pitch, FOV, ht1) + camera_height, 2)
    CBH1 = round(pitch_correct(pitch, FOV, hb1) + camera_height, 2)
    hb2 = find_height(4160-CT2, row.Distance,
                      focal_length_mm, sensor_height_mm)
    ht2 = find_height(4160-CB2, row.Distance,
                      focal_length_mm, sensor_height_mm)
    CTH2 = round(pitch_correct(pitch, FOV, ht2) + camera_height, 2)
    CBH2 = round(pitch_correct(pitch, FOV, hb2) + camera_height, 2)
    df2.at[row.Index, 'Time'] = row.Date_Time
    df2.at[row.Index, 'distance_to_cloud'] = row.Distance
    df2.at[row.Index, 'CT1'] = CTH2
    df2.at[row.Index, 'CB1'] = CBH1
    df2.at[row.Index, 'CTP1'] = CB2
    df2.at[row.Index, 'CBP1'] = CT1
    df2.at[row.Index, 'X1'] = X1
    df2.at[row.Index, 'W1'] = W1
    df2.at[row.Index, 'CT2'] = CTH1
    df2.at[row.Index, 'CB2'] = CBH2
    df2.at[row.Index, 'CTP2'] = CB1
    df2.at[row.Index, 'CBP2'] = CT2
    df2.at[row.Index, 'X2'] = X2
    df2.at[row.Index, 'W2'] = W2
    df2.at[row.Index, 'MAXCTH'] = np.nanmax([CTH1, CTH2])

# -------------------------------- Plots and CSV ----------------------------- #

# Configuring plot font size
plt.rcParams['font.size'] = 16

# Plotting and saving various scatter plots
# Each plot corresponds to different aspects of cloud height, base, distance,
# and pixel coordinates

# Plot 1: Cloud Top Height 1 vs. Time
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['CT1'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud top height in photo for ' + date +
              '\n camera: ' + str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' + date_to_use +
            '_camera_'+str(camera) + '_cloud_top_height1.png')
plt.close('all')

# Plot 2: Max Cloud Top Height vs. Time
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['MAXCTH'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud top height in photo for ' + date +
              '\n camera: ' + str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' + date_to_use +
            '_camera_' + str(camera) + '_cloud_top_height_max_height.png')
plt.close('all')

# Plot 3: Cloud Top Height2 vs. Time
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['CT2'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud top height in photo for '+date +
              '\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_cloud_top_height2.png')
plt.close('all')

# Plot 4: Max Cloud Base Height1 vs. Time
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['CB1'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud base height in photo for '+date +
              '\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_cloud_base_height1.png')
plt.close('all')

# Plot 5: Max Cloud Base Height2 vs. Time
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['CB2'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud base height in photo for '+date +
              '\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_cloud_base_height2.png')
plt.close('all')

# Plot 6: Distance to cloud vs. Time
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['distance_to_cloud'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Distance (km)')
axs.set_title('Distance between camera and max optical depth for  '+date +
              '\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_distance_vs_time.png')
plt.close('all')

# Plot 7: hotrizontal point of cloud box vs. Time
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['X1']+df2['W1']/2, marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('pixels from left corner')
axs.set_title('Horizontal pixel co-ordinate for center of box round clound  '
              + date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera) +
            '_horizontal_movement_vs_time1.png')
plt.close('all')

# Plot 8: hotrizontal point of cloud box vs. Time
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['X2']+df2['W2']/2, marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('pixels from left corner')
axs.set_title('Horizontal pixel co-ordinate for center of box round clound  '
              + date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera) +
            '_horizontal_movement_vs_time2.png')
plt.close('all')

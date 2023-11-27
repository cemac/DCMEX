#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 11:03:18 2023

@author: earhbu
"""

import pandas as pd
import math
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
# Variables

# Camera info
# https://www.digicamdb.com/specs/canon_eos-6d-mark-ii/
#
# 26,200,000 photosites (pixels) on this area. distance between pixels: 5.73 µm
# 861.6 mm2
#
# Distance from camera to object (m)
D = 1000
# Focal Length (mm)
F = 50  # find out accuracy
# Sensor height = 35.9 x 24 mm so 24mm high
SH = 24
# Image width x height: 6240 x 4160


# Height = (Distance to Object x Object height on sensor) / Focal Length

"""
Fundamentals of Photonics, Bahaa E. A. Saleh and Malvin Carl Teich, 2007, 
FOV diagram
Introduction to Modern Optics, Author: Grant R. Fowles,
Dover Publications, 1989 - thin lens equations

"""

date_to_use = '2022-07-31'
date= '31-07-2022'
camera=2
storage = '/home/users/hburns/GWS/DCMEX/users/hburns/'
# Sensor dimensions
sensor_height_mm = 24.0
sensor_width_mm = 35.9

# Focal length in mm
focal_length_mm = 50.0

# Calculate FOV angles in radians
fov_horizontal_rad = 2 * math.atan(sensor_width_mm / (2 * focal_length_mm))
fov_vertical_rad = 2 * math.atan(sensor_height_mm / (2 * focal_length_mm))

# Convert FOV angles to degrees
fov_horizontal_deg = math.degrees(fov_horizontal_rad)
fov_vertical_deg = math.degrees(fov_vertical_rad)

print("FOV Horizontal Angle:", fov_horizontal_deg, "degrees")
print("FOV Vertical Angle:", fov_vertical_deg, "degrees")
FOV = fov_vertical_deg


# List of camera locations from files, dates, corresponding frame, 
#ring colours and distances
camlon = -106.898107
camlat = 34.023982


cam_details = storage+'/camera_details.csv'
cam_df = pd.read_csv(cam_details)
# Camera height above sea level
camera_height = 1.45

cloud_distances = pd.read_csv(
    storage+'/results/'+date_to_use+'/Cloud_distnaces.csv')
cloud_pixels = pd.read_csv(
    storage+'/results/'+date_to_use+'/cloud_pixels.csv')
date_format_distances = '%Y-%m-%dT%H:%M:%S'
date_format_pixels = '%Y-%m-%dT%H%M'
date_object_distances = datetime.strptime(
    cloud_distances.Datetimes.iloc[0].split('.')[0], date_format_distances)
date_object_pixels = datetime.strptime(
    date_to_use+'T'+str(cloud_pixels.Times.iloc[0]), date_format_pixels)

cloud_distances['Date_Time'] = pd.to_datetime(cloud_distances.Datetimes)
cloud_pixels['Date_Time'] = ''
for index, row in cloud_pixels.iterrows():
    cloud_pixels['Date_Time'].iloc[index] = datetime.strptime(
        date_to_use+'T'+str(cloud_pixels.Times.iloc[index]), date_format_pixels)

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

condition = (cloud_pixels['Distance'] > 30) | (cloud_pixels['Distance'] < 10)
df_filtered = cloud_pixels[~condition]


def find_height(P, D, F, SH):
    OHS = find_OHS(P, SH)
    H = (D * 10**3 * OHS) / F
    return round(H / 10**3, 2)

# Object height on sensor =  (Sensor height (mm) × Object height (pixels)) 
#                                      / Sensor height (pixels)
# Sensor height (px) = Sensor height (mm) / distance between pixels
# SHP = 24*10**-3 / 5.73*10**-6
# SHP = 4188


def find_OHS(P, SH):
    SHP = 4188
    OHS = SH * P / SHP
    return OHS


def pitch_correct(P, FOV, h):
    # See diagram for agles a, b and c
    a = 90 - P - FOV/2
    b = 180 - 90 - FOV/2
    # image plane incline from vertical
    c = 180 - a - b
    # x is true height, h is height on incled place
    x = h * math.cos(math.radians(c))
    return x


filtered_df = cam_df[(cam_df['Date'] == date) & (cam_df['camera'] == camera)]
yaw_degrees = filtered_df.yaw.values[0]
pitch = filtered_df.pitch.values[0]
camera_height = filtered_df.height.values[0]/1000
# Read in distance in km
df_filtered = df_filtered.reset_index(drop=True)
df2 = pd.DataFrame(index=range(len(df_filtered)), columns=[
                   'Time', 'distance_to_cloud', 'CT', 'CT2'])
i = 0
for row in df_filtered.itertuples():
    CT2 = 4500-row.CT
    CT1 = 4500-row.CT1
    CT = np.nanmax([CT2, CT1])
    h = find_height(CT, row.Distance, F, SH)
    h2 = find_height(CT, 24, F, SH)
    CB1 = round(pitch_correct(pitch, FOV, h) + camera_height, 2)
    CB2 = round(pitch_correct(pitch, FOV, h2) + camera_height, 2)
    df2.at[row.Index, 'Time'] = row.Date_Time
    df2.at[row.Index, 'distance_to_cloud'] = row.Distance
    df2.at[row.Index, 'CT'] = CB1
    df2.at[row.Index, 'CT2'] = CB2


# df2.to_csv('results/cloud_heights_using_min_distance_pitch_corr_pc_max_cloudtop_distance.csv')

fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['CT'], marker='o',)

plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_cloud_top_height.png')
plt.scatter(df2['Time'], df2['distance_to_cloud'], marker='o',)

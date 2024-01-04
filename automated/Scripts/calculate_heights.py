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
from matplotlib.dates import DateFormatter

import sys
# Extract arguments
camera = int(sys.argv[1])
date_to_use = str(sys.argv[2])

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

#date_to_use = '2022-07-31'
parts= date_to_use.split('-')
date= parts[-1]+'-'+parts[1]+'-'+parts[0]
#camera=2
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


cloud_distances = pd.read_csv(
    storage+'/results/'+date_to_use+'/Cloud_distnaces_camera_'+str(camera)+'.csv')
cloud_pixels = pd.read_csv(
    storage+'/results/'+date_to_use+'/cloud_pixels_camera_'+str(camera)+'.csv')
date_format_distances = '%Y-%m-%dT%H:%M:%S'
date_format_pixels = '%Y-%m-%dT%H%M%S'
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



try:
    condition = (cloud_pixels['Distance'] > 30) | (cloud_pixels['Distance'] < 10)
except TypeError:
    cloud_pixels = cloud_pixels[cloud_pixels != 'no cloud']
    cloud_pixels['Distance'] = pd.to_numeric(cloud_pixels['Distance'])
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
                   'Time', 'distance_to_cloud', 'CT1', 'CT2', 'CB1','CB2','CTP1','CTP2',
                   'CBP1','CTBP2', 'W1','W2', 'X1','X2','MAXCTH'])
i = 0
for row in df_filtered.itertuples():
    CT2 = row.CT1
    CT1 = row.CT2
    W1=row.W1
    X1=row.CX1
    CB1=row.CB1 
    W2=row.W2
    X2=row.CX2
    CB2=row.CB2
    hb1 = find_height(4160-CT1, row.Distance, F, SH)
    ht1 = find_height(4160-CB1, row.Distance, F, SH)
    CTH1 = round(pitch_correct(pitch, FOV, ht1) + camera_height, 2)
    CBH1 = round(pitch_correct(pitch, FOV, hb1) + camera_height, 2)
    hb2 = find_height(4160-CT2, row.Distance, F, SH)
    ht2 = find_height(4160-CB2, row.Distance, F, SH)
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

df2.to_csv(storage+'/results/'+date_to_use+'/'+date_to_use+'_camera_'+str(camera)+'_cloud_top_heights.csv')
plt.rcParams['font.size'] = 16
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['CT1'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud top height in photo for '+date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_cloud_top_height1.png')
plt.close('all')
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['MAXCTH'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud top height in photo for '+date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_cloud_top_height_max_height.png')
plt.close('all')
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['CT2'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud top height in photo for '+date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_cloud_top_height2.png')
plt.close('all')

fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['CB1'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud base height in photo for '+date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_cloud_base_height1.png')
plt.close('all')

fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['CB2'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Height (km)')
axs.set_title('Max estimated cloud base height in photo for '+date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_cloud_base_height2.png')
plt.close('all')
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['distance_to_cloud'], marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('Distance (km)')
axs.set_title('Distance between camera and max optical depth for  '+date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_distance_vs_time.png')
plt.close('all')
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['X1']+df2['W1']/2, marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('pixels from left corner')
axs.set_title('Horizontal pixel co-ordinate for center of box round clound  '+date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_horizontal_movement_vs_time1.png')
plt.close('all')
fig, axs = plt.subplots(figsize=(20, 20))
plt.scatter(df2['Time'], df2['X2']+df2['W2']/2, marker='o',)
axs.xaxis.set_major_formatter(DateFormatter('%H:%M'))
axs.set_xlabel('Time')
axs.set_ylabel('pixels from left corner')
axs.set_title('Horizontal pixel co-ordinate for center of box round clound  '+date+'\n camera: '+str(camera))
plt.xticks(rotation=45)
plt.savefig(storage + 'results/' + date_to_use + '/' +
            date_to_use + '_camera_'+str(camera)+'_horizontal_movement_vs_time2.png')
plt.close('all')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optical Depth Plotter

Filter out cirrus cloud below 3.6
Plot camera FOV, orography and find location on max optical depth in that area
 
 
"""

import xarray as xr
import glob
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.path import Path
from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point
import numpy as np
import haversine as hs
import math
import sys
# Extract arguments
camera = int(sys.argv[1])
date_to_use = str(sys.argv[2])
#date_to_use = '2022-07-31'
#camera=2
storage = '/home/users/hburns/GWS/DCMEX/users/hburns/'
imgroot = str(storage + "images/FOV_on_optical_depth/"+date_to_use+'/camera/'+str(camera)+'/')
dataroot = '/gws/nopw/j04/dcmex/data'
if not os.path.exists(imgroot):
       # If it doesn't exist, create it
       os.makedirs(imgroot)

if not os.path.exists(storage+'results/'+date_to_use+'/'):
       os.makedirs(storage+'results/'+date_to_use+'/')

cam_details = storage + '/camera_details.csv'
cam_df = pd.read_csv(cam_details)
if camera==2:
    fnames = glob.glob(
    dataroot+'/stereocams/'+date_to_use+'/secondary_red/amof-cam-2-'+date_to_use+'-*.jpg')
else:
 fnames = glob.glob(
    dataroot+'/stereocams/'+date_to_use+'/primary_blue/amof-cam-1-'+date_to_use+'-*.jpg')
yaw_error = 10

date_list = []
date_list2 = []
time_list = []
for file_name in fnames:
    parts = os.path.splitext(os.path.basename(file_name))[0].split('-')
    yyyy, mm, dd, hhmmss = parts[3], parts[4], parts[5], parts[6]
    date_time = datetime.strptime(
        f'{yyyy}-{mm}-{dd}-{hhmmss}', "%Y-%m-%d-%H%M%S")
    # Formatting date and time
    formatted_date = date_time.strftime("%d-%m-%Y")
    formatted_date2 = date_time.strftime("%Y-%m-%d")
    formatted_time = date_time.strftime("%H%M")
    date_list.append(formatted_date)
    date_list2.append(formatted_date2)
    time_list.append(formatted_time)

date_fnames = list(set(date_list))
date_fnames2 = list(set(date_list2))    
filtered_df = cam_df[(cam_df['Date'] == date_fnames[0])
                     & (cam_df['camera'] == camera)]
yaw_degrees = filtered_df.yaw.values[0]
camlat = filtered_df.camlat.values[0]
camlon = filtered_df.camlon.values[0]
print('camlat: ', camlat)
print('camlon: ', camlon)
# Set Paramers to read in satelite data regridded into lat lon
lat1 = 33.75
lat2 = 34.25
lon1 = -107.5
lon2 = -106.8
file_root = "/gws/nopw/j04/dcmex/data/GOES16pcrgd/Magda/"
channel1 = "ABI-L2-CODC/"
# channel2 = "ABI-L2-ACMC/"
fname_root = "/*/OR_ABI-L2-CODC-M6_G16*_select_pcrgd.nc"
# fname_root2 = "/OR_ABI-*_G16_*_select_rgd.nc"
optical_depth_threshold = 3.6
# Orography file
orog_file = '/gws/nopw/j04/dcmex/users/dfinney/data/globe_orog_data_NM.nc'
orog = xr.open_dataset(orog_file)['topo'].sel(
    X=slice(lon1, lon2), Y=slice(lat1, lat2))
southbaldy = [33.99, -107.19]
MRO = [33.98481699, -107.18926709]
CB = [34.0248532,-106.9267249]

# TODO: create csv of colours and kms to load in

data = []

for date in date_fnames2:
    date_path = date.replace('-', '/', 3)
    rad = xr.open_mfdataset(glob.glob(file_root + channel1 + date_path + fname_root),
                            combine="nested", concat_dim="t")["var1"].sel(lon=slice(lon1, lon2),
                                                                          lat=slice(lat1, lat2))
    data.append(rad)


"Fundamentals of Photonics, Bahaa E. A. Saleh and Malvin Carl Teich, 2007, FOV diagram"
"Introduction to Modern Optics, Author: Grant R. Fowles, Dover Publications, 1989 - thin lens equations"
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


def FOV_area(camlat, camlon, yaw_degrees, fov_horizontal_deg):
    # Field of view angle (in degrees)
    fov_degrees = fov_horizontal_deg

    # Calculate the endpoints of the field of view
    fov_radius = 0.35  # Adjust this value for the desired FOV radius on the map
    fov_start = yaw_degrees - fov_degrees / 2
    fov_end = yaw_degrees + fov_degrees / 2

    # Convert the yaw angles to radians
    fov_start_rad = np.radians(fov_start)
    fov_end_rad = np.radians(fov_end)

    # Calculate the FOV coordinates
    fov_x = [camlon] + [camlon + fov_radius *
                        np.sin(a) for a in np.linspace(fov_start_rad, fov_end_rad, 100)]
    fov_y = [camlat] + [camlat + fov_radius *
                        np.cos(a) for a in np.linspace(fov_start_rad, fov_end_rad, 100)]
    return fov_x, fov_y


def find_max_in_fov(data, fov_x, fov_y):
    # Define a grid of latitude and longitude within the FOV area
    lons = data.coords['lon'].values
    lats = data.coords['lat'].values
    # Define a grid of latitude and longitude within the FOV area
    polygon_points = list(zip(fov_x, fov_y))
    polygon_path = Path(polygon_points)
    x_grid, y_grid = np.meshgrid(lons, lats)

    # Flatten the grid arrays to 1D arrays
    x_flat = x_grid.flatten()
    y_flat = y_grid.flatten()

    # Create an array of (x, y) points
    points = np.column_stack((x_flat, y_flat))

    # Check if each point is within the polygon
    mask = polygon_path.contains_points(points)

    # Reshape the mask back to 2D
    mask = mask.reshape(x_grid.shape)

    # Apply the mask to your original array
    # Replace original_array with your actual array that you want to mask
    masked_array = data.values.copy()
    masked_array[~mask] = np.nan  # Set values outside the polygon to NaN
    maxlat, maxlon = np.unravel_index(
        np.nanargmax(masked_array), masked_array.shape)

    return maxlat, maxlon

# Fuction to plot 1km rings from


def geodesic_point_buffer(lat, lon, km):
    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres
    return transform(project, buf).exterior.coords.xy


def plotring(data, ax, camlat, camlon, yaw, title):
    mask = data >= 3.6
    masked_data = data.where(mask, other=np.nan)
    masked_data.plot.pcolormesh(x="lon", y="lat", ax=ax, levels=[
                                3.6, 9.4, 23, 60, 100], cbar_kwargs={'label': 'optical depth'})
    day1 = data.values
    valid_data = ~np.all(np.isnan(day1), axis=0)
    lons = data.coords['lon'].values
    lats = data.coords['lat'].values
    fov_x, fov_y = FOV_area(camlat, camlon, yaw, fov_horizontal_deg)
    # Yaw is plus minus 5 deg so add 10 deg to FOV
    fov_xp5, fov_yp5 = FOV_area(
        camlat, camlon, yaw, fov_horizontal_deg +2*yaw_error)
    try:
        test = np.unravel_index(np.nanargmax(day1), day1.shape)
        if test:
            print('cloud found')
    except:
        print('no cloud in area')
        D = 'no cloud'
        maxlat_2 = 'none'
        maxlon_2 = 'none'
        orog.plot.contour(x="X", y="Y", colors='k', ax=ax,
                          levels=[2400, 2500, 2800, 3300])
        ax.fill(fov_x, fov_y, color='silver', alpha=0.3, label='Field of View')
        ax.fill(fov_xp5, fov_yp5, color='silver',
                alpha=0.2, label='Field of View Error')
        ax.scatter(camlon, camlat, color='r',
                   marker='D', s=400, label='Camera')
        ax.scatter(MRO[1], MRO[0], marker='+', color='k', s=200, label='MRO')
        ax.scatter(CB[1], CB[0], marker='+', color='k', s=150, label='CB')
        ax.scatter(southbaldy[1], southbaldy[0], marker='^',
                   color='k', label='South Baldy peak', s=200)
        ax.set_title(title, fontsize='15')
        ax.set_xticks(np.arange(camlon - 1, camlon + 1, 0.1))
        ax.set_yticks(np.arange(camlat - 1, camlat + 1, 0.1))
        ax.set_xlim(lon1, lon2)
        ax.set_ylim(lat1, lat2)
        # Add a legend
        ax.legend()
        return D, maxlat_2, maxlon_2

    orog.plot.contour(x="X", y="Y", colors='k', ax=ax,
                      levels=[2400, 2500, 2800, 3300])
    ax.fill(fov_x, fov_y, color='silver', alpha=0.3, label='Field of View')
    ax.fill(fov_xp5, fov_yp5, color='silver',
            alpha=0.2, label='Field of View Error')

    try:
        maxlat_2, maxlon_2 = find_max_in_fov(data, fov_xp5, fov_yp5)
        ax.scatter(lons[maxlon_2], lats[maxlat_2], marker='x',
                   color='r', s=400, label='Max optical depth')
        D = hs.haversine((lats[maxlat_2], lons[maxlon_2]), (camlat, camlon))

    except:
        print('no cloud in FOV')
        D = 'no cloud'
        maxlat_2 = 'none'
        maxlon_2 = 'none'
    
    ax.scatter(camlon, camlat, color='r', marker='D', s=400, label='Camera')
    ax.scatter(MRO[1], MRO[0], marker='+', color='k', s=200, label='MRO')
    ax.scatter(CB[1], CB[0], marker='+', color='k', s=150, label='CB')
    ax.scatter(southbaldy[1], southbaldy[0], marker='^',
               color='k', label='South Baldy peak', s=200)
    ax.set_title(title, fontsize='15')
    ax.set_xticks(np.arange(camlon - 1, camlon + 1, 0.1))
    ax.set_yticks(np.arange(camlat - 1, camlat + 1, 0.1))
    ax.set_xlim(lon1, lon2)
    ax.set_ylim(lat1, lat2)
    # Add a legend
    ax.legend()
    return D, maxlat_2, maxlon_2


plt.rcParams['font.size'] = 16

distances = []
datetimes = []
CT_lat = []
CT_lon = [] 
# for j in range(len(data):
for i in range(len(data[0].t)):
    timestamp = data[0].t[i].values
    hour = np.datetime64(timestamp, 'h').item().hour
    if int(time_list[0])/100 < hour < int(time_list[-1])/100:
        fig, axs = plt.subplots(figsize=(20, 20))
        proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
        D, maxlat_2, maxlon_2 = plotring(data[0][i], axs, camlat, camlon, yaw_degrees,
                                         np.datetime_as_string(data[0].t[i].data, unit='m'))
        distances.append(D)
        datetimes.append(data[0].t[i].data)
        CT_lat.append(maxlat_2)
        CT_lon.append(maxlon_2)
        plt.tight_layout()
        plt.savefig(
            imgroot+np.datetime_as_string(data[0].t[i].data, unit='m')+'.png')
        plt.close ('all')

cloud_distances = pd.DataFrame({'Datetimes': datetimes, 'Distance': distances, 'CT_lat': CT_lat, 'CT_lon':CT_lon})
cloud_distances.to_csv(
    storage+'results/'+date_to_use+'/Cloud_distnaces_camera_'+str(camera)+'.csv')

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
import xarray as xr
import glob
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.path import Path
import pyproj
import numpy as np
import haversine as hs
import math
import sys

# Extract arguments
camera = int(sys.argv[1])
date_to_use = str(sys.argv[2])
# Path to area to write images and results to
storage = '/home/users/hburns/GWS/DCMEX/users/hburns/'
# Path to write created images
imgroot = str(storage + "images/FOV_on_optical_depth/" +
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

if not os.path.exists(storage+'results/'+date_to_use+'/'):
    os.makedirs(storage+'results/'+date_to_use+'/')

# Select file names based on camera and date
if camera == 2:
    fnames = glob.glob(dataroot + '/stereocams/' + date_to_use +
                       '/secondary_red/amof-cam-2-' + date_to_use + '-*.jpg')
else:
    fnames = glob.glob(dataroot + '/stereocams/' + date_to_use +
                       '/primary_blue/amof-cam-1-' + date_to_use + '-*.jpg')

# Extract date and time from file names
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

# Filter unique dates
date_fnames = list(set(date_list))
date_fnames2 = list(set(date_list2))


# Load data related to camera details
filtered_df = cam_df[(cam_df['Date'] == date_fnames[0])
                     & (cam_df['camera'] == camera)]
yaw_degrees = filtered_df.yaw.values[0]
camlat = filtered_df.camlat.values[0]
camlon = filtered_df.camlon.values[0]
print('camlat: ', camlat)
print('camlon: ', camlon)

# ------------------- Optical Depth Data ------------------------------------ #
# Set Paramers to read in satelite data regridded into lat lon
lat1 = 33.75
lat2 = 34.25
lon1 = -107.5
lon2 = -106.8

file_root = "/gws/nopw/j04/dcmex/data/GOES16pcrgd/Magda/"
channel1 = "ABI-L2-CODC/"
fname_root = "/*/OR_ABI-L2-CODC-M6_G16*_select_pcrgd.nc"

# Orography file
orog_file = '/gws/nopw/j04/dcmex/users/dfinney/data/globe_orog_data_NM.nc'
orog = xr.open_dataset(orog_file)['topo'].sel(
    X=slice(lon1, lon2), Y=slice(lat1, lat2))
southbaldy = [33.99, -107.19]
MRO = [33.98481699, -107.18926709]
CB = [34.0248532, -106.9267249]


# Create an empty list to store satellite data
data = []

for date in date_fnames2:
    date_path = date.replace('-', '/', 3)
    # Open and append satellite data to the list
    rad = xr.open_mfdataset(glob.glob(file_root + channel1 + date_path + fname_root),
                            combine="nested", concat_dim="t")["var1"].sel(lon=slice(lon1, lon2),
                                                                          lat=slice(lat1, lat2))
    data.append(rad)


# -------------------------------- Calculate FOV ---------------------------- #
# Define camera parameters (sensor dimensions, focal length, FOV angles)
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

# ----------------------Functions-------------------------------------------- #

# Function to calculate FOV area


def FOV_area(camlat, camlon, yaw_degrees, fov_horizontal_deg):
    """
Calculate the coordinates of a field of view (FOV) area on a map based on the camera's position and orientation.

Parameters:
- camlat (float): Latitude of the camera's position.
- camlon (float): Longitude of the camera's position.
- yaw_degrees (float): Yaw angle of the camera in degrees (rotation around the vertical axis).
- fov_horizontal_deg (float): Horizontal field of view angle in degrees.

Returns:
- fov_x (list): List of x-coordinates representing the FOV polygon.
- fov_y (list): List of y-coordinates representing the FOV polygon.

Note:
- The FOV is assumed to be a segment of a circular area on the map.
- The FOV is calculated based on the camera's position, orientation, and specified horizontal field of view angle.
- The FOV is discretized into 100 points for smoother visualization.

Usage Example:
```python
cam_latitude = 37.7749
cam_longitude = -122.4194
cam_yaw = 45.0
cam_fov = 60.0

fov_x, fov_y = FOV_area(cam_latitude, cam_longitude, cam_yaw, cam_fov)
```

Adjust the `fov_radius` parameter inside the function to control the radius of the FOV on the map.
"""
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
                        np.sin(a) for a in np.linspace(fov_start_rad,
                                                       fov_end_rad, 100)]
    fov_y = [camlat] + [camlat + fov_radius *
                        np.cos(a) for a in np.linspace(fov_start_rad,
                                                       fov_end_rad, 100)]
    return fov_x, fov_y


def find_max_in_fov(data, fov_x, fov_y):
    """
Find the maximum value and corresponding location within a specified field of view (FOV) on a gridded dataset.

Parameters:
- data (numpy.ndarray): The 2D array of values representing the dataset, e.g., temperature, humidity.
- fov_x (list): List of x-coordinates defining the FOV polygon.
- fov_y (list): List of y-coordinates defining the FOV polygon.

Returns:
- maxlat (int): Index of the latitude with the maximum value within the FOV.
- maxlon (int): Index of the longitude with the maximum value within the FOV.

Note:
- The function uses a given FOV defined by its x and y coordinates to identify the grid points within the FOV.
- The maximum value and its corresponding location within the FOV are then determined.
- The input data array is masked, setting values outside the FOV to NaN.

Usage Example:
```python
# Assuming 'temperature_data' is a 2D array representing temperature values
fov_x, fov_y = FOV_area(cam_latitude, cam_longitude, cam_yaw, cam_fov)
maxlat, maxlon = find_max_in_fov(temperature_data, fov_x, fov_y)
```

Replace 'temperature_data' with the actual 2D array representing your dataset.
"""
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


def plotring(data, ax, camlat, camlon, yaw, title):
    """
Plot a ring around a camera's field of view (FOV) and highlight cloud-related information.

Parameters:
- data (xr.DataArray): 2D array of values representing the dataset.
- ax (matplotlib.axes._subplots.AxesSubplot): Matplotlib axes for plotting.
- camlat (float): Latitude of the camera's position.
- camlon (float): Longitude of the camera's position.
- yaw (float): Yaw angle of the camera in degrees.
- title (str): Title for the plot.

Returns:
- D (float or str): Haversine distance between the camera and the maximum optical depth point, or 'no cloud' if no cloud is found.
- maxlat_2 (int or str): Index of the latitude with the maximum optical depth within the FOV, or 'none' if no cloud is found.
- maxlon_2 (int or str): Index of the longitude with the maximum optical depth within the FOV, or 'none' if no cloud is found.

Note:
- The function visualizes the FOV, FOV error, and cloud-related information on a plot.
- It uses a threshold value of 3.6 for cloud detection.
- The FOV is discretized into 100 points for smoother visualization.
- The function returns information about the maximum optical depth point within the FOV.

Usage Example:
```python
# Assuming 'data' is an xarray DataArray representing optical depth values
# and 'ax' is a Matplotlib axes
D, maxlat_2, maxlon_2 = plotring(data, ax, camlat, camlon, yaw, "Optical Depth Plot")
```

Replace 'data', 'camlat', 'camlon', 'yaw', and 'title' with your specific values.
"""
    mask = data >= 3.6
    masked_data = data.where(mask, other=np.nan)
    masked_data.plot.pcolormesh(x="lon", y="lat", ax=ax, levels=[
                                3.6, 9.4, 23, 60, 100],
                                cbar_kwargs={'label': 'optical depth'})
    day1 = data.values
    lons = data.coords['lon'].values
    lats = data.coords['lat'].values
    fov_x, fov_y = FOV_area(camlat, camlon, yaw, fov_horizontal_deg)
    # Yaw is plus minus the YAW error
    fov_xp5, fov_yp5 = FOV_area(
        camlat, camlon, yaw, fov_horizontal_deg + 2*yaw_error)
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


# -------------- Loop through times to create plots ------------------------- #
# Set font size for plots
plt.rcParams['font.size'] = 16

# Lists to store distances, datetimes, and coordinates
distances = []
datetimes = []
CT_lat = []
CT_lon = []
# Loop through the time dimension of the satellite data
for i in range(len(data[0].t)):
    timestamp = data[0].t[i].values
    hour = np.datetime64(timestamp, 'h').item().hour
    if int(time_list[0])/100 < hour < int(time_list[-1])/100:
        # Create a new plot for each timestamp
        fig, axs = plt.subplots(figsize=(20, 20))
        proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
        # Plot the data, FOV, and additional annotations
        D, maxlat_2, maxlon_2 = plotring(data[0][i], axs, camlat, camlon,
                                         yaw_degrees,
                                         np.datetime_as_string(data[0].t[i].data,
                                                               unit='m'))
        # Append results to lists
        distances.append(D)
        datetimes.append(data[0].t[i].data)
        CT_lat.append(maxlat_2)
        CT_lon.append(maxlon_2)
        # Save the plot as an image
        plt.tight_layout()
        plt.savefig(
            imgroot+np.datetime_as_string(data[0].t[i].data, unit='m')+'.png')
        plt.close('all')

# Create a DataFrame from the collected results and save it to a CSV file
cloud_distances = pd.DataFrame(
    {'Datetimes': datetimes, 'Distance': distances, 'CT_lat': CT_lat,
     'CT_lon': CT_lon})
cloud_distances.to_csv(
    storage + 'results/' + date_to_use + '/Cloud_distnaces_camera_'
    + str(camera) + '.csv')

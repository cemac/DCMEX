#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
..moduleauthor: Helen (CEMAC)


..description: A python Script that Estimates Cloud Heigh
    :copyright: © 2022 University of Leeds.
..usage:
    ./cloudheightestimator.py

..args: <will take file names in future>

..Requirements:


"""
import pandas as pd

# Variables

# Camera info
# https://www.digicamdb.com/specs/canon_eos-6d-mark-ii/
#
# 26,200,000 photosites (pixels) on this area. distance between pixels: 5.73 µm
# 861.6 mm2
#
# Distance from camera to object (m)
D = 1
# Focal Length (mm)
F = 24 # find out accuracy https://www.ephotozine.com/equipment/item/panasonic-lumix-dmc-tz27-6762
# Sensor height = so 24mm high
# 1/2.3-type High Sensitivity MOS Sensor https://www.techradar.com/how-to/sensor-sizes-explained-what-you-need-to-know
# Dimensions: approx. 6.12 x 4.62mm
SH = 4.62
# Image width x height: 6240 x 4160

# Camera height above sea level
camera_height = 0
# Height = (Distance to Object x Object height on sensor) / Focal Length

# equations from: https://www.scantips.com/lights/fieldofviewmath.html might need to find a text book referece!


def find_height(P, D, F, SH):
    OHS = find_OHS(P, SH)
    H = (D  * OHS) / F
    return round(H , 2)

# Object height on sensor =  (Sensor height (mm) × Object height (pixels)) / Sensor height (pixels)
# Sensor height (px) = https://www.ephotozine.com/equipment/item/panasonic-lumix-dmc-tz27-6762
# SHP =
# SHP = 3016

def find_OHS(P, SH):
    SHP = 3016
    OHS = (SH * P / SHP)
    return OHS


# Read in distance in km
df = pd.read_csv('pixel_data/object_distances.csv')
dfw = pd.read_csv('pixel_data/object_distances_wonky.csv')
df2 = pd.DataFrame(columns=['object', 'actual_size', 'size', 'error'])
df3 = pd.DataFrame(columns=['object', 'actual_size', 'size', 'error', 'error_est'])
for i in range(4):
    h2 = find_height(df["pixel_height_top"][i], (df["distance_min"][i]-6)*10,
                     F, SH) + camera_height
    h1 = find_height(df["pixel_height_bottom"][i], (df["distance_min"][i]-6)*10,
                     F, SH) + camera_height
    size = h2 - h1
    pixel_error = (df["pixel_range"][i] / (df["pixel_height_top"][i]-df["pixel_height_bottom"][i]))*100
    distance_error = (0.5/  df["distance_min"][i])*100
    error = pixel_error + distance_error
    df2.loc[i] = [df["object"][i],df["actual_height"][i], size, error]
    h2 = find_height(dfw["pixel_height_top"][i], (dfw["distance_min"][i])*10,
                     F, SH) + camera_height
    h1 = find_height(dfw["pixel_height_bottom"][i], (dfw["distance_min"][i])*10,
                     F, SH) + camera_height
    sizew = h2 - h1
    pixel_error = (dfw["pixel_range"][i] / (dfw["pixel_height_top"][i]-dfw["pixel_height_bottom"][i]))*100
    distance_error = (1/  dfw["distance_min"][i])*100
    errorw = pixel_error + distance_error
    error_a = ((sizew-df["actual_height"][i])/df["actual_height"][i])*100
    df3.loc[i] = [df["object"][i],df["actual_height"][i], sizew, error_a, errorw]

df2.to_csv('results/object_heights.csv')
df3.to_csv('results/object_heights_wonky.csv')

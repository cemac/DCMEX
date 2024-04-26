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
import math
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
F = 50 # find out accuracy
# Sensor height = 35.9 x 24 mm so 24mm high
SH = 24
# Image width x height: 6240 x 4160

# Camera height above sea level
camera_height = 1.45
# Height = (Distance to Object x Object height on sensor) / Focal Length

# equations from: https://www.scantips.com/lights/fieldofviewmath.html might need to find a text book referece!


def find_height(P, D, F, SH):
    OHS = find_OHS(P, SH)
    # Height = (Distance to Object x Object height on sensor) / Focal Length
    H = (D * 10**3 * OHS) / F
    return round(H / 10**3, 2)

# Object height on sensor =  (Sensor height (mm) × Object height (pixels)) / Sensor height (pixels)
# Sensor height (px) = Sensor height (mm) / distance between pixels
# SHP = 24*10**-3 / 5.73*10**-6
# SHP = 4188

def find_OHS(P, SH):
    SHP = 4188
    # Object height on sensor =  (Sensor height (mm) × Object height (pixels)) / Sensor height (pixels)
    OHS = (SH * P / SHP)
    return OHS


def find_tc(P):
    # Field of View
    FOV = 27
    # theta_cld_from_ceter = 0.5 * FOV / num pixels from center
    theta_c = 0.5 * FOV / (P - (4160/2) )
    return(theta_c)

# Read in distance in km
df = pd.read_csv('pixel_data/known_objects.csv')
df2 = pd.DataFrame(columns=['Time', 'distance', 'est_height','pitch_corrected', 'actual_height'])
for i in range(2):

    h = find_height(df["pixel_height"][i], (df["GD_min"][i]) * 1000,
                     F, SH)
    theta_c = df["pitch"][i] + find_tc(h)
    # h_pitch_corrected = d * tan (theta_c) + cam height
    # This doesn't work - I think because with a pitched camera the image height is incline
    # the next script pitch correct uses this 
    h_pc = df["GD_min"][i] *1000 * math.tan(math.radians(theta_c)) + camera_height * 1000

    df2.loc[i] = [df["object"][i],df["GD_max"][i],h + camera_height * 1000,h_pc,df["actual_height"][i]]


df2.to_csv('results/known_objects_height.csv')

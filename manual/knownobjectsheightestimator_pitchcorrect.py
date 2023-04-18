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
import geopy.distance
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

FOV = 27

# equations from: https://www.scantips.com/lights/fieldofviewmath.html might need to find a text book referece!

# List of camera locations from files, dates, corresponding frame, ring colours and distances
camlon = -106.898107
camlat = 34.023982

def find_height(P, D, F, SH):
    OHS = find_OHS(P, SH)
    H = (D * 10**3 * OHS) / F
    return round(H / 10**3, 2)

# Object height on sensor =  (Sensor height (mm) × Object height (pixels)) / Sensor height (pixels)
# Sensor height (px) = Sensor height (mm) / distance between pixels
# SHP = 24*10**-3 / 5.73*10**-6
# SHP = 4188

def find_OHS(P, SH):
    SHP = 4188
    OHS = (SH * P / SHP)
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


# Read in distance in km
df = pd.read_csv('pixel_data/known_objects.csv')
df2 = pd.DataFrame(columns=['Time', 'distance (km)', 'est_height','pitch_corrected', 'actual_height'])
for i in range(2):
    # fight height on inclinded image plane
    D = geopy.distance.geodesic((camlat,camlon),(df["lat"][i],df["lon"][i]))
    h = find_height(df["pixel_height"][i], D.m,
                     F, SH)
    # correct for pitch
    h_pc = pitch_correct(df["pitch"][i], FOV, h)

    df2.loc[i] = [df["object"][i],round(D.km,2), int(h + camera_height * 1000),
                  int(h_pc + camera_height * 1000), df["actual_height"][i]]


df2.to_csv('results/known_objects_pitch_corrected_success.csv')

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


# Pitch Adjustment
def pitch_adjust(F,P,H, camera_height):
    # https://www.researchgate.net/publication/287515600_Height_estimation_from_a_single_camera_view
    pnew = (F * (  H * math.cos(math.radians(P)) - F * math.sin(math.radians(P))) /
         ( H * math.sin(math.radians(P)) + F * math.cos(math.radians(P)) ) )
    return pnew

# Read in distance in km
df = pd.read_csv('pixel_data/known_objects.csv')
df2 = pd.DataFrame(columns=['Time', 'distance', 'est_height', 'actual_height'])
for i in range(2):
    pnew =  pitch_adjust(F, -df["pitch"][i], df["pixel_height"][i], camera_height)
    # Calculate height with out pixel adjust
    h = find_height(df["pixel_height"][i], (df["GD_min"][i])*1000,
                     F, SH) + camera_height * 1000
    print(pnew)
    print(df["pixel_height"][i])
    df2.loc[i] = [df["object"][i],df["GD_max"][i],h,df["actual_height"][i]]


df2.to_csv('results/known_objects_height.csv')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
..moduleauthor: Helen (CEMAC)


..description: A python Script that Estimates Cloud Heigh
    :copyright: © 2022 University of Leeds.
..usage:
    ./cloudheightestimator.py <pixel> <distance>

..args: pixles distance

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
D = 1000
# Focal Length (mm)
F= 50
# Sensor height = 35.9 x 24 mm so 24mm high
SH = 24
# Image width x height: 6240 x 4160

# Height = (Distance to Object x Object height on sensor) / Focal Length
def find_height(P,D,F,SH):
  OHS=find_OHS(P,SH)
  H = (D*OHS)/F
  return H

# Object height on sensor =  (Sensor height (mm) × Object height (pixels)) / Sensor height (pixels)
# SHP = 24*10**-3 / 5.73*10**-6
def find_OHS(P,SH):
    SHP = 4188
    OHS = (SH * P / SHP)
    return OHS

df=pd.read_csv('cloudheights.csv')
df2=pd.DataFrame(columns=['Time','CB1','CB2','CB3','CT1','CT2','CT3'])
df3=pd.DataFrame(columns=['Time','CB1','CB2','CB3','CT1','CT2','CT3'])
for i in range(5):
    CB1=find_height(df["CB1"][i],df["distance_min"][i],F,SH)
    CB2=find_height(df["CB3"][i],df["distance_min"][i],F,SH)
    CB3=find_height(df["CB3"][i],df["distance_min"][i],F,SH)
    CT1=find_height(df["CT1"][i],df["distance_min"][i],F,SH)
    CT2=find_height(df["CT2"][i],df["distance_min"][i],F,SH)
    CT3=find_height(df["CT3"][i],df["distance_min"][i],F,SH)
    df2.loc[i]=[df["Time"][0],CB1,CB2,CB3,CT1,CT2,CT3]

for i in range(5):
    CB1=find_height(df["CB1"][i],df["distance_max"][i],F,SH)
    CB2=find_height(df["CB3"][i],df["distance_max"][i],F,SH)
    CB3=find_height(df["CB3"][i],df["distance_max"][i],F,SH)
    CT1=find_height(df["CT1"][i],df["distance_max"][i],F,SH)
    CT2=find_height(df["CT2"][i],df["distance_max"][i],F,SH)
    CT3=find_height(df["CT3"][i],df["distance_max"][i],F,SH)
    df3.loc[i]=[df["Time"][0],CB1,CB2,CB3,CT1,CT2,CT3]

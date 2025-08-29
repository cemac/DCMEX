#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python: 3.8 Jasmin NERC servers
Project: DCMEX

Description:
This script calculates the height of clouds based on pixel position, distance, and pitch.

Usage: python calculate_heights.py <pixels> <distance> <pitch>
where: 
- pixels is the y-pixel position of the cloud on the photo (0,0) being left hand corner (int)
- distance is the distance to the cloud in kilometers (float)
- pitch is the pitch of the camera in degrees (float)

Example: python calculate_heights.py 1000 2.5 30

"""

import sys
import math
import pandas as pd

class CloudHeightCalculator:
    """
    A class to calculate the height of clouds.

    Attributes:
        pixels (int): y-pixel position of the cloud on the photo (0,0 being the left hand corner).
        distance (float): Distance to the cloud in kilometers.
        pitch (float): Pitch of the camera in degrees.
    """

    def __init__(self, pixels, distance, pitch):
        """
        Initialize the CloudHeightCalculator with pixel position, distance, and pitch.

        Args:
            pixels (int): y-pixel position of the cloud on the photo.
            distance (float): Distance to the cloud in kilometers.
            pitch (float): Pitch of the camera in degrees.
        """
        self.pixels =4188- int(pixels)
        self.distance = float(distance)
        self.pitch = float(pitch)
        self.focal_length_mm = 50.0
        self.sensor_height_mm = 24.0
        self.sensor_width_mm = 35.9
        self.storage = '/gws/nopw/j04/dcmex/users/hburns'
        self.cam_details_path = f'{self.storage}/camera_details.csv'
        self.cam_df = pd.read_csv(self.cam_details_path)
        # Object height on sensor =  (Sensor height (mm) × Object height (pixels))
        #                                      / Sensor height (pixels)
        # Sensor height (px) = Sensor height (mm) / distance between pixels
        # sensor_height_pixels = 24*10**-3 / 5.73*10**-6
        # sensor_height_pixels = 4188
        self.sensor_height_pixels = 4188
        self.calculate_fov()

    def calculate_height(self):
        """
        Calculate the height of the cloud.

        This method uses the pixel position, distance to calculate the raw height of the cloud, 
        then corrects this height based on the camera's pitch.

        Returns:
            float: The corrected height of the cloud.
        """
        height_raw = self.find_height(self.pixels, self.distance)
        height_corrected = self.pitch_correct(self.pitch, height_raw)
        return height_corrected
    
    def calculate_fov(self):
        """
        Calculate the vertical field of view in degrees.
        """
        vertical_rad = 2 * math.atan(self.sensor_height_mm / (2 * self.focal_length_mm))
        self.fov_vertical_deg = math.degrees(vertical_rad)

    def find_height(self, P, Distance):
        """
        Calculate the height of an object given its pixel position on the photo.

        Args:
            P (int): y-pixel position of the object on the photo.
            Distance (float): Distance to the object in km

        Returns:
            float: Height of the object in kilometers (rounded to 2 decimal places).
        """
        OHS = self.find_OHS(P)
        height = (Distance * 10**3 * OHS) / self.focal_length_mm
        return round(height / 10**3, 2)

    def find_OHS(self, P):
        """
        Calculate the Object Height on Sensor.

        Args:
            P (int): Pixel position of the object on the photo.

        Returns:
            float: Object Height on Sensor.
        """
        OHS = self.sensor_height_mm * P / self.sensor_height_pixels
        return OHS

    def pitch_correct(self, P, h):
        """
        Correct the pitch of the camera based on angles and height.

        Args:
            P (float): pitch.
            h (float): Height on the inclined plane.

        Returns:
            float: True height after pitch correction.
        """
        # See diagram for angles a, b and c
        a = 90 - P - self.fov_vertical_deg / 2
        b = 180 - 90 - self.fov_vertical_deg / 2
        # image plane incline from vertical
        c = 180 - a - b
        # x is true height, h is height on inclined place
        x = h * math.cos(math.radians(c))
        return x

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python calculate_heights.py <pixels> <distance> <pitch>")
        print("Example: python calculate_heights.py 888 27 14.5")
        sys.exit(1)
    if len(sys.argv) == 4:
        pixels, distance, pitch = sys.argv[1:]
    elif len(sys.argv) == 5:
        pixels, distance, pitch, date = sys.argv[1:]
        
    calculator = CloudHeightCalculator(pixels, distance, pitch)
    height_corrected = calculator.calculate_height()
    print(height_corrected, ' above camera')
    print(height_corrected+1.45, ' asl')

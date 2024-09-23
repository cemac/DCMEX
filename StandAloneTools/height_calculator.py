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
        self.pixels = int(pixels)
        self.distance = float(distance)
        self.pitch = float(pitch)

    def calculate_height(self):
        """
        Calculate the height of the cloud.

        This method uses the pixel position, distance to calculate the raw height of the cloud, 
        then corrects this height based on the camera's pitch.

        Returns:
            float: The corrected height of the cloud.
        """
        height_raw = self.camera.find_height(self.pixels, self.distance)
        height_corrected = self.camera.pitch_correct(self.pitch, height_raw)
        return height_corrected

class Camera:
    """
    A class to model the camera properties and operations.

    Attributes:
        focal_length_mm (float): Focal length of the camera lens in millimeters.
        sensor_height_mm (float): Height of the camera sensor in millimeters.
        sensor_width_mm (float): Width of the camera sensor in millimeters.
        fov_vertical_deg (float): Vertical field of view in degrees.
    """

    def __init__(self):
        """
        Initialize the Camera with default properties.
        # Camera info
        # https://www.digicamdb.com/specs/canon_eos-6d-mark-ii/
        #
        # 26,200,000 photosites (pixels) on this area. distance between pixels: 5.73 µm
        # 861.6 mm2
        #
        # Sensor height = 35.9 x 24 mm so 24mm high
        # Image width x height: 6240 x 4160
        """
        self.focal_length_mm = 50.0
        self.sensor_height_mm = 24.0
        self.sensor_width_mm = 35.9
        # Object height on sensor =  (Sensor height (mm) × Object height (pixels))
        #                                      / Sensor height (pixels)
        # Sensor height (px) = Sensor height (mm) / distance between pixels
        # sensor_height_pixels = 24*10**-3 / 5.73*10**-6
        # sensor_height_pixels = 4188
        self.sensor_height_pixels = 4188
        self.calculate_fov()

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
        x = h * math.cos(c)
        return x

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python calculate_heights.py <pixels> <distance> <pitch>")
        sys.exit(1)

    pixels, distance, pitch = sys.argv[1:]
    calculator = CloudHeightCalculator(pixels, distance, pitch)
    height_corrected = calculator.calculate_height()
    print(height_corrected)

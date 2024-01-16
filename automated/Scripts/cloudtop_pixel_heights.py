"""
python script cloudtop_pixel_heights.py

author: helen burns CEMAC UoL 2023
python: 3.8 Jasmin NERC servers
project: DCMEX

Description

Usage: python     cloudtop_pixel_heights.py <camera> <date>
where
camera : interger 1 or 2
date : string 'yyyy-mm-dd'

this script takes cloud photos from storage location for that day, checks if
the optical depth script returned if there was a cloud that day. If so then
uses OpenCV to find the edge of the cloud and draws a box over the two largest
contours and writes information to csv file.

"""

# import modules
import glob
import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import color
from skimage import io
import cv2

# Extract arguments
camera = int(sys.argv[1])
date_to_use = str(sys.argv[2])

# Set Constants for edge detection:
# How white vs grey (this might need to be set by trial and error)    
WHITENESS_THRESHOLD = 115
# line thickness of box
THICKNESS = 16
# The part of every photo is just ground set to 0 if whole photo is cloud
NOTSKY = 3350

# Set file paths and directories
storage = '/home/users/hburns/GWS/DCMEX/users/hburns/'
imgroot = os.path.join(storage, "images/cloud_top_heights", 
                        date_to_use, str(camera))
result_root = os.path.join(storage, 'results', date_to_use)
dataroot = '/gws/nopw/j04/dcmex/data'

# Create directories if they don't exist
if not os.path.exists(imgroot):
    # If it doesn't exist, create it
    os.makedirs(imgroot)

if not os.path.exists(storage+'results/'+date_to_use+'/'):
    os.makedirs(storage+'results/'+date_to_use+'/')

# Read camera details from CSV
cam_details = storage + '/camera_details.csv'
cam_df = pd.read_csv(cam_details)

# Choose file paths based on the camera
if camera == 2:
    fnames = glob.glob(dataroot + '/stereocams/' + date_to_use +
                       '/secondary_red/amof-cam-2-' + date_to_use + '-*.jpg')
else:
    fnames = glob.glob(dataroot + '/stereocams/' + date_to_use +
                       '/primary_blue/amof-cam-1-' + date_to_use + '-*.jpg')

# Extract date and time information from file names
date_list = []
time_list = []
hour_list = []
for file_name in fnames:
    parts = os.path.splitext(os.path.basename(file_name))[0].split('-')
    yyyy, mm, dd, hhmmss = parts[3], parts[4], parts[5], parts[6]
    date_time = datetime.strptime(f"{yyyy}-{mm}-{dd}-{hhmmss}",
                                  "%Y-%m-%d-%H%M%S")
    # Formatting date and time
    formatted_date = date_time.strftime("%Y-%m-%d")
    formatted_time = date_time.strftime("%H%M%S")
    formatted_hours = date_time.strftime("%H%M")
    date_list.append(formatted_date)
    time_list.append(formatted_time)
    hour_list.append(formatted_hours)

# Extract unique dates and create datetime objects
date_fnames = list(set(date_list))
datetime_objects = [datetime.strptime(f'{date} {time[:2]}:{time[2:]}',
                                      '%Y-%m-%d %H:%M') 
                    for date, time in zip(date_list, hour_list)]


# Read cloud distances CSV and convert Date_Time column to datetime
cloud_distances = pd.read_csv(storage + '/results/' + date_to_use +
                              '/Cloud_distnaces_camera_' + str(camera) +
                              '.csv')
cloud_distances['Date_Time'] = pd.to_datetime(cloud_distances.Datetimes)


# -------- Functions to select photos with clouds and detect edges ---------  # 
# Function to find the index of the closest date in an array
def find_closest_index(target_date, date_array):
    """
Find the index of the closest date in a sorted array.

Parameters:
- target_date (str or numpy.datetime64): The target date for which to find 
  the closest match.
- date_array (numpy.ndarray): A sorted array of dates.

Returns:
- int: The index of the closest date in the array.

Note:
- This function assumes that date_array is sorted.
- If date_array is not sorted, the result may not be correct.
- If there are duplicate dates, the index of the first occurrence with the 
  minimum absolute difference is returned.
- The function uses numpy's argmin function to find the index.

Example:

>>> closest_index = find_closest_index(target_date, date_array)
>>> print(closest_index)
Output: 1 (index of '2022-07-25:17:33')
"""
    return np.argmin(np.abs(target_date - date_array))


# Convert datetime_objects to numpy array for indexing
array1 = np.array([np.datetime64(dt) for dt in datetime_objects])
closest_indices = [find_closest_index(dt, cloud_distances.Date_Time.values)
                   for dt in array1]

# Function to find contours in an image
def find_contours(fname, title, WHITENESS_THRESHOLD, THICKNESS, NOSKY):
    """
    Find contours in an image and draw bounding boxes around detected objects.

    Parameters:
    - fname (str): File path of the image to analyze.
    - title (str): Prefix for the saved images.

    Returns:
    - Tuple[int, int, int, int, int, int, int, int]: Coordinates and dimensions of the detected bounding boxes.
      (y_max, h_max, y_max1, h_max1, x_max, x_max1, w_max, w_max1)

    Notes:
    - This function loads an image, applies edge detection, and identifies contours to find objects.
    - Bounding boxes are drawn around detected objects, and the resulting image is saved.
    - Adjust the WHITENESS_THRESHOLD and thickness values as needed.
    - If no bounding box is detected, a tuple of zeros is returned.

    Example:
    >>> find_contours('path/to/image.jpg', 'output_prefix')
    Output: (y_max, h_max, y_max1, h_max1, x_max, x_max1, w_max, w_max1)
    """
    # Load the image and convert to grayscale
    img_grey = color.rgb2gray(io.imread(glob.glob(fname)[0]))
    img = Image.open(glob.glob(fname)[0])
    
    # Create a mask based on pixel whiteness
    mask = np.all(img > WHITENESS_THRESHOLD, axis=-1)
    img_grey[~mask] = 0
    img_grey[NOSKY::, :] = 0

    # Use NumPy for operations instead of PIL and CV2
    cv_grey = cv2.GaussianBlur(img_grey.astype(np.uint8) * 255, (5, 5), 0)
    edges = cv2.Canny(cv_grey, 0, 200)

    # Find contours and sort by area
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, 
                                   cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Initialize variables for bounding box with the maximum area
    bounding_box_image = img.copy()
    max_max = 0

    for contour in sorted_contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        rectangle_area = w * h

        if rectangle_area >= max_max:
            x_max1, y_max1, w_max1, h_max1 = x, y, w, h
            max_max = rectangle_area

    try:
        # Draw a rectangle around the detected object with the maximum area
        cv2.rectangle(bounding_box_image, (x_max1, y_max1), 
                      (x_max1 + w_max1, y_max1 + h_max1), (0, 255, 0), 
                      THICKNESS)
    except cv2.error:
        # Return zeros if no bounding box is detected
        return 0, 0, 0, 0, 0, 0, 0, 0

    # Find the second-largest bounding box
    max_c = 0

    for contour in sorted_contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        rectangle_area = w * h

        if rectangle_area >= max_c:
            if rectangle_area < max_max:
                x_max, y_max, w_max, h_max = x, y, w, h
                max_c = rectangle_area

    # Draw a rectangle around the second-largest detected object
    cv2.rectangle(bounding_box_image, (x_max, y_max), 
                  (x_max + w_max, y_max + h_max), (0, 255, 0), THICKNESS)

    # Save the image with bounding boxes
    cv2.imwrite('output/' + title + '_cloud_box.png', bounding_box_image)

    return y_max, h_max, y_max1, h_max1, x_max, x_max1, w_max, w_max1

# ---- loop though the list of files to find the clouds and generate DF ----- #

# Lists to store cloud pixel information
cb1 = []
ct1 = []
cb2 = []
ct2 = []
cx1 = []
cx2 = []
w1 = []
w2 = []
time_list2 = []
index = 0
# Loop through the images and find cloud pixel information
for i in range(len(fnames)):
    check = cloud_distances.Distance.iloc[closest_indices[index]]
    index += 1

    if check == 'none' or check == 'no cloud':
        continue
    try:
        check = float(check)
        if check > 30 or check < 10:
            continue
    except TypeError:
        print('error:', check)
        continue
    fig, axs = plt.subplots(figsize=(20, 20))
    cloudbox1 = find_contours(fnames[i],
                              date_fnames[0] + '-' + time_list[i] + '_',
                              WHITENESS_THRESHOLD, THICKNESS, NOTSKY)
    y_max, h_max, y_max1, h_max1, x_max, x_max1, w_max, w_max1 = cloudbox1
    time_list2.append(time_list[index-1])
    cb1.append(y_max1)
    ct1.append(y_max1+h_max1)
    cb2.append(y_max)
    ct2.append(y_max+h_max)
    cx1.append(x_max)
    cx2.append(x_max1)
    w1.append(w_max)
    w2.append(w_max1)
    plt.close('all')
# https://gis.stackexchange.com/questions/289044/creating-buffer-circle-x-kilometers-from-point-using-python

# Create DataFrame and save to CSV
cloud_pixels = pd.DataFrame({'Times': time_list2, 'CB1': cb1, 'CB2': cb2,
                             'CT1': ct1, 'CT2': ct2, 'CX1': cx1, 'CX2': cx2,
                             'W1': w1, 'W2': w2})

cloud_pixels.to_csv(os.path.join(result_root,
                                 f'cloud_pixels_camera_{camera}.csv'))
                               

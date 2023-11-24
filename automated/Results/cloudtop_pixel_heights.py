import glob
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.path import Path
import numpy as np
import math
import pandas as pd
from PIL import Image
from skimage import feature
from skimage import color
from skimage import io
import cv2 as cv2
fnames = glob.glob('/home/users/hburns/GWS/DCMEX/data/stereocams/2022-07-31/secondary_red/amof-cam-2-2022-07-31-*.jpg')
date_list = []
time_list = []
for file_name in fnames:
    parts = os.path.splitext(os.path.basename(file_name))[0].split('-')
    yyyy,mm,dd,hhmmss = parts[3], parts[4], parts[5], parts[6] 
    date_time = datetime.strptime(f"{yyyy}-{mm}-{dd}-{hhmmss}", "%Y-%m-%d-%H%M%S")
    # Formatting date and time
    formatted_date = date_time.strftime("%Y-%m-%d")
    formatted_time = date_time.strftime("%H%M")
    date_list.append(formatted_date)
    time_list.append(formatted_time)

date_fnames = list(set(date_list))
cam_details = '/home/users/hburns/GWS/DCMEX/users/hburns/camera_details.csv'
cam_df = pd.read_csv(cam_details)
#fnames=fnames[0:10]


def find_contours(fname,ax, title):
    #img=Image.open(glob.glob(fname1)[0])
    img_grey=color.rgb2gray(io.imread(glob.glob(fname)[0]))
    whiteness_threshold =115
    img=Image.open(glob.glob(fname)[0])
    mask = np.all(np.array(img) > whiteness_threshold, axis =-1)
    #mask = np.all(np.array(img) > whiteness_threshold, axis =-1)
    img_masked = img_grey.copy()
    img_masked[~mask]=0
    img_masked[3350::,:]=0
    #img_masked[0:1000,:]=0
    cv2.imwrite('cloud_mask.png',img_masked)
    #plt.imshow(img_masked, cmap="gray")
    cv_grey= cv2.imread('cloud_mask.png',cv2.IMREAD_GRAYSCALE)
    blurred_image = cv2.GaussianBlur(cv_grey, (5, 5), 0)
    edges=cv2.Canny(blurred_image*255,0,200)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
    bounding_box_image = cv2.imread(glob.glob(fname)[0]).copy()
    max_max = 0 
    for contour in sorted_contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        rectanglea = w*h
        if rectanglea >= max_max:
            x_max1 = x
            y_max1 = y
            w_max1 = w
            h_max1 = h
            max_max = rectanglea
    thickness = 16  # Adjust this value to control the thickness of the drawn contour 
    cv2.rectangle(bounding_box_image, (x_max1, y_max1), (x_max1 + w_max1, y_max1 + h_max1), (0, 255, 0), thickness)
    # Save the image with the three largest bounding boxes
    max = 0
    for contour in sorted_contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        rectanglea = w*h
        if rectanglea >= max:
            if rectanglea < max_max:
                x_max = x
                y_max = y
                w_max = w
                h_max = h
                max = rectanglea
    thickness = 16  # Adjust this value to control the thickness of the drawn contour 
    cv2.rectangle(bounding_box_image, (x_max, y_max), (x_max + w_max, y_max + h_max), (0, 255, 0), thickness)
    # Save the image with the three largest bounding boxes
    
    # Save the image with bounding boxes
    cv2.imwrite('cloud_box.png', bounding_box_image)
    cloud_edge2=Image.open('cloud_box.png')
    ax.imshow(cloud_edge2)
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig('/home/users/hburns/GWS/DCMEX/users/hburns/images/cloud_top_heights/' + title + 'cloud_box.png')
    return y_max, h_max, y_max1, h_max1
#cloud_edge2=Image.open('cloud_edge2.png')
#plt.imshow(cloud_edge2)

cb1=[]
ct1=[]
cb2=[]
ct2=[]
for i in range(len(fnames)):
    fig, axs = plt.subplots(figsize=(20, 20))
    y_max, h_max, y_max1, h_max1 = find_contours(fnames[i],axs,date_fnames[0]+'-'+time_list[i] + '_')
    cb1.append(y_max1)
    ct1.append(y_max1+h_max1)
    cb2.append(y_max)
    ct2.append(y_max+h_max)
    plt.close ('all')
# https://gis.stackexchange.com/questions/289044/creating-buffer-circle-x-kilometers-from-point-using-python

cloud_pixels = pd.DataFrame({'Times': time_list, 'CB1': cb1, 'CB': cb2, 'CT1': ct1, 'CT': ct2,})
cloud_pixels.to_csv('/home/users/hburns/GWS/DCMEX/users/hburns/cloud_pixels.csv')

import glob
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from skimage import color
from skimage import io
import cv2 as cv2
import sys
# Extract arguments
camera = int(sys.argv[1])
date_to_use = str(sys.argv[2])



#date_to_use = '2022-07-22'
storage = '/home/users/hburns/GWS/DCMEX/users/hburns/'
#camera=1
imgroot = str(storage + "images/cloud_top_heights/"+date_to_use+'/'+str(camera)+'/')
dataroot = '/gws/nopw/j04/dcmex/data'
if not os.path.exists(imgroot):
       # If it doesn't exist, create it
       os.makedirs(imgroot)

if not os.path.exists(storage+'results/'+date_to_use+'/'):
       os.makedirs(storage+'results/'+date_to_use+'/')

cam_details = storage + '/camera_details.csv'
cam_df = pd.read_csv(cam_details)


if camera==2:
    fnames = glob.glob(
    dataroot+'/stereocams/'+date_to_use+'/secondary_red/amof-cam-2-'+date_to_use+'-*.jpg')
else:
    fnames = glob.glob(
    dataroot+'/stereocams/'+date_to_use+'/primary_blue/amof-cam-1-'+date_to_use+'-*.jpg')


date_list = []
time_list = []
hour_list = []
for file_name in fnames:
    parts = os.path.splitext(os.path.basename(file_name))[0].split('-')
    yyyy,mm,dd,hhmmss = parts[3], parts[4], parts[5], parts[6] 
    date_time = datetime.strptime(f"{yyyy}-{mm}-{dd}-{hhmmss}", "%Y-%m-%d-%H%M%S")
    # Formatting date and time
    formatted_date = date_time.strftime("%Y-%m-%d")
    formatted_time = date_time.strftime("%H%M%S")
    formatted_hours = date_time.strftime("%H%M")
    date_list.append(formatted_date)
    time_list.append(formatted_time)
    hour_list.append(formatted_hours)

date_fnames = list(set(date_list))
datetime_objects = []
for date, time in zip(date_list, hour_list):
    # Combine date and time strings
    datetime_str = f'{date} {time[:2]}:{time[2:]}'
    
    # Parse the combined string into a datetime object
    dt_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
    
    # Append the datetime object to the list
    datetime_objects.append(dt_object)

cloud_distances = pd.read_csv(
    storage+'/results/'+date_to_use+'/Cloud_distnaces_camera_'+str(camera)+'.csv')
cloud_distances['Date_Time'] = pd.to_datetime(cloud_distances.Datetimes)

def find_closest_index(target_date, date_array):
    return np.argmin(np.abs(target_date - date_array))

array1 = np.array([np.datetime64(dt) for dt in datetime_objects])
closest_indices = [find_closest_index(dt, cloud_distances.Date_Time.values) for dt in array1]



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
    try:
           cv2.rectangle(bounding_box_image, (x_max1, y_max1), (x_max1 + w_max1, y_max1 + h_max1), (0, 255, 0), thickness)
    except:
            x_max1 = 0
            y_max1 = 0
            w_max1 = 0
            h_max1 = 0
            x_max = 0
            y_max = 0
            w_max = 0
            h_max = 0
            print('no box')
            return y_max, h_max, y_max1, h_max1, x_max, x_max1, w_max, w_max1
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
    cv2.imwrite(imgroot+'/'+title+'_cloud_box.png', bounding_box_image)
    cloud_edge2=Image.open('cloud_box.png')
    #ax.imshow(cloud_edge2)
    #ax.set_title(title)
    #plt.tight_layout()
    #plt.savefig(imgroot+'/'+title+'_cloud_box.png')
    return y_max, h_max, y_max1, h_max1, x_max, x_max1, w_max, w_max1
#cloud_edge2=Image.open('cloud_edge2.png')
#plt.imshow(cloud_edge2)


cb1=[]
ct1=[]
cb2=[]
ct2=[]
cx1=[]
cx2=[]
w1=[]
w2=[]
time_list2=[]
index=0
for i in range(len(fnames)):
    check=cloud_distances.Distance.iloc[closest_indices[index]]
    index+=1
    #print(cloud_distances.Distance.iloc[closest_indices[index]])
    #bin off data
    if check == 'none' or check=='no cloud':
        continue
    try:   
           check = float(check)
           if check >30 or check <10:
                  continue
    except TypeError:
           print('error:', check)
           continue
    fig, axs = plt.subplots(figsize=(20, 20))    
    y_max, h_max, y_max1, h_max1,x_max,x_max1,w_max, w_max1 = find_contours(fnames[i],axs,date_fnames[0]+'-'+time_list[i] + '_')
    time_list2.append(time_list[index-1])
    cb1.append(y_max1)
    ct1.append(y_max1+h_max1)
    cb2.append(y_max)
    ct2.append(y_max+h_max)
    cx1.append(x_max)
    cx2.append(x_max1)
    w1.append(w_max)
    w2.append(w_max1)
    plt.close ('all')
# https://gis.stackexchange.com/questions/289044/creating-buffer-circle-x-kilometers-from-point-using-python

cloud_pixels = pd.DataFrame({'Times': time_list2, 'CB1': cb1, 'CB2': cb2,
                             'CT1': ct1, 'CT2': ct2,'CX1': cx1, 'CX2': cx2, 
                             'W1': w1, 'W2': w2})
#cloud_pixels.to_csv('/home/users/hburns/GWS/DCMEX/users/hburns/cloud_pixels.csv')
cloud_pixels.to_csv(
    storage+'results/'+date_to_use+'/cloud_pixels_camera_'+str(camera)+'.csv')
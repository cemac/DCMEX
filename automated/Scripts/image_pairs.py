import os
import datetime
from shutil import copyfile
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
import sys
# Extract arguments                                                                                                                                                                                                
camera = int(sys.argv[1])
date_to_use = str(sys.argv[2])

storage = '/home/users/hburns/GWS/DCMEX/users/hburns/'
folder1 = storage+'images/cloud_top_heights/'+date_to_use+'/'+str(camera)+'/'
folder2 = storage+'images/FOV_on_optical_depth/'+date_to_use+'/camera/'+str(camera)+'/'
folder3 = storage+'images/image_pairs/'+date_to_use+'/'+str(camera)+'/'
cloud_heights=pd.read_csv(storage+'/results/'+date_to_use+'/'+date_to_use+'_camera_'+str(camera)+'_cloud_top_heights.csv')
# Ensure folder3 exists
if not os.path.exists(folder3):
    os.makedirs(folder3)

# Function to extract timestamp from file name in folder1
def extract_timestamp_folder1(filename):
    #2022-07-18-164244_
    timestamp_str = filename.split('_')[0]#[0:-2]
    return datetime.datetime.strptime(timestamp_str, '%Y-%m-%d-%H%M%S')

# Function to extract timestamp from file name in folder2
def extract_timestamp_folder2(filename):
    timestamp_str = filename.split('.')[0]
    return datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M')


# Iterate through files in folder1
for file1 in os.listdir(folder1):
    if file1.endswith('.png'):
        timestamp1 = extract_timestamp_folder1(file1)
        # Iterate through files in folder2 to find the closest match
        closest_file2 = None
        closest_time_difference = float('inf')

        for file2 in os.listdir(folder2):
            if file2.endswith('.png'):
                timestamp2 = extract_timestamp_folder2(file2)
                time_difference = abs((timestamp1 - timestamp2).total_seconds())
                if time_difference < closest_time_difference:
                    closest_time_difference = time_difference
                    closest_file2 = file2

        # Load images and create a subplot
        if closest_file2 is not None:
            file1_path = os.path.join(folder1, file1)
            file2_path = os.path.join(folder2, closest_file2)
            filtered_df = cloud_heights[(pd.to_datetime(cloud_heights['Time']) == timestamp1)]
            timestamp_nearest = extract_timestamp_folder2(closest_file2)
            img1 = Image.open(file1_path)
            img2 = Image.open(file2_path)
            # Create a new figure with subplots
            plt.figure(figsize=(40, 20))              
            # Display the images in subplots
            plt.subplot(1, 2, 1)
            plt.imshow(img1)
            try:
                plt.plot(filtered_df.W.values[0]/2+filtered_df.X.values[0], filtered_df.CTP.values[0], 'o',color='r')
                plt.text(filtered_df.W.values[0]/2+filtered_df.X.values[0], filtered_df.CTP.values[0],str(filtered_df.CT.values[0])+' km',fontsize=40, color='k')
                plt.plot(filtered_df.W.values[0]/2+filtered_df.X.values[0], filtered_df.CBP.values[0], 'o',color='r')
                plt.text(filtered_df.W.values[0]/2+filtered_df.X.values[0], filtered_df.CBP.values[0],str(filtered_df.CB.values[0])+' km',fontsize=40, color='k')
            except IndexError:
                print('no box')
            plt.title(str(timestamp1)+'\n boxed cloud image')
            plt.subplot(1, 2, 2)
            plt.imshow(img2)
            plt.axis('off')  # Turn off axes
            plt.title(str(timestamp_nearest)+'\n optical depth')
            plt.savefig(folder3+timestamp1.strftime('%Y-%m-%dT%H:%M')+'.png')
            plt.close('all')

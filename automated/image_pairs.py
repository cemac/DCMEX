import os
import datetime
from shutil import copyfile
from PIL import Image
import matplotlib.pyplot as plt

folder1 = '/home/users/hburns/GWS/DCMEX/users/hburns/images/cloud_top_heights/'
folder2 = '/home/users/hburns/GWS/DCMEX/users/hburns/images/FOV_on_optical_depth/'
folder3 = '/home/users/hburns/GWS/DCMEX/users/hburns/images/image_pairs/'

# Ensure folder3 exists
if not os.path.exists(folder3):
    os.makedirs(folder3)

# Function to extract timestamp from file name in folder1
def extract_timestamp_folder1(filename):
    timestamp_str = filename.split('_')[0]
    return datetime.datetime.strptime(timestamp_str, '%Y-%m-%d-%H%M')

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
            timestamp_nearest = extract_timestamp_folder2(closest_file2)
            img1 = Image.open(file1_path)
            img2 = Image.open(file2_path)

            # Create a new figure with subplots
            plt.figure(figsize=(40, 20))

            # Display the images in subplots
            plt.subplot(1, 2, 1)
            plt.imshow(img1)
            plt.axis('off')  # Turn off axes
            plt.title(str(timestamp1)+'\n boxed cloud image')

            plt.subplot(1, 2, 2)
            plt.imshow(img2)
            plt.axis('off')  # Turn off axes
            plt.title(str(timestamp_nearest)+'\n optical depth')

            plt.savefig(folder3+timestamp1.strftime('%Y-%m-%dT%H:%M')+'.png')
            
            plt.close('all')

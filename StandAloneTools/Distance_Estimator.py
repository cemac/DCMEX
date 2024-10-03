import xarray as xr
import os
import math
import glob
from matplotlib.path import Path
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.interpolate import griddata
import pyproj
import haversine as hs
from functools import partial
from shapely.ops import transform
from shapely.geometry import Point

class CloudOpticalDepthProcessor:
    """
    A class to process cloud optical depth data, calculate Field of View (FOV) for a camera,
    and plot cloud-related information.

    Attributes:
    ----------
    file_name: str
        Path to the satellite file to process.
    camera: int
        Camera number.
    date_to_use: str
        Date to use for data filtering and storage path.
    storage: str
        Path to storage location for images and results.
    yaw_error: float
        Error margin for the YAW parameter (default: 10).
    optical_depth_threshold: float
        Threshold for optical depth (default: 3.6).
    cam_df: pd.DataFrame
        DataFrame with camera details.

    Methods:
    -------
    load_camera_details():
        Load camera details from the CSV file.
    extract_file_metadata():
        Extract date and time metadata from the satellite file name.
    setup_directories():
        Create necessary directories for saving images and results.
    calculate_fov():
        Calculate the Field of View (FOV) area for the camera.
    plot_fov():
        Plot a ring around the camera’s FOV and highlight cloud information.
    process_file():
        Process the satellite file and generate the FOV plot.
    """

    def __init__(self, file_name):
        """
        Initialize CloudOpticalDepthProcessor with input arguments.
        """
        self.file_name = file_name
        self.storage = '/home/users/hburns/GWS/DCMEX/users/hburns/'
        self.dataroot = '/gws/nopw/j04/dcmex/data'
        self.yaw_error = 10
        self.optical_depth_threshold = 3.6
        self.cam_details_path = f'{self.storage}/camera_details.csv'
        self.cam_df = pd.read_csv(self.cam_details_path)
        self.lat1 = 33.75
        self.lat2 = 34.25
        self.lon1 = -107.5
        self.lon2 = -106.8
        self.date_fnames,self.date_to_use, self.time_to_use,self.camera = self.extract_file_metadata()
        sensor_height_mm = 24.0
        sensor_width_mm = 35.9

        # Focal length in mm
        focal_length_mm = 50.0

        # Calculate FOV angles in radians
        fov_horizontal_rad = 2 * math.atan(sensor_width_mm / (2 * focal_length_mm))
        fov_vertical_rad = 2 * math.atan(sensor_height_mm / (2 * focal_length_mm))

        # Convert FOV angles to degrees
        self.fov_horizontal_deg = math.degrees(fov_horizontal_rad)
        self.fov_vertical_deg = math.degrees(fov_vertical_rad)

       
        

    def extract_file_metadata(self):
        """
        Extract date and time metadata from the file name.
        """
        parts = os.path.splitext(os.path.basename(self.file_name))[0].split('-')
        yyyy, mm, dd, hhmmss = parts[3], parts[4], parts[5], parts[6]
        date_time = datetime.strptime(f'{yyyy}-{mm}-{dd}-{hhmmss}', "%Y-%m-%d-%H%M%S")
        camera = parts[2]
        return date_time.strftime("%d-%m-%Y"), date_time.strftime("%Y-%m-%d"), date_time.strftime("%H%M"), camera

    def load_camera_details(self):
        """
        Load camera details for the specific date and camera number.
        """
        filtered_df = self.cam_df[(self.cam_df['Date'] == self.date_fnames) & (self.cam_df['camera'] == int(self.camera))]
        yaw_degrees = filtered_df.yaw.values[0]
        camlat = filtered_df.camlat.values[0]
        camlon = filtered_df.camlon.values[0]
        return yaw_degrees, camlat, camlon

    def calculate_fov(self, camlat, camlon, yaw_degrees, fov_horz = None):
        """
        Calculate the coordinates of the Field of View (FOV) area on the map.
        """
        fov_radius = 0.35  
        fov_start = yaw_degrees - fov_horz / 2
        fov_end = yaw_degrees + fov_horz / 2
        fov_x = [camlon] + [camlon + fov_radius * np.sin(a) for a in np.linspace(np.radians(fov_start), np.radians(fov_end), 100)]
        fov_y = [camlat] + [camlat + fov_radius * np.cos(a) for a in np.linspace(np.radians(fov_start), np.radians(fov_end), 100)]
        return fov_x, fov_y

    def find_max_in_fov(self, data, fov_x, fov_y):
        """
        Find the maximum value and corresponding location within a specified field of view (FOV) on a gridded dataset.

        Parameters:
        - data (numpy.ndarray): The 2D array of values representing the dataset, e.g., temperature, humidity.
        - fov_x (list): List of x-coordinates defining the FOV polygon.
        - fov_y (list): List of y-coordinates defining the FOV polygon.

        Returns:
        - maxlat (int): Index of the latitude with the maximum value within the FOV.
        - maxlon (int): Index of the longitude with the maximum value within the FOV.

        Note:
        - The function uses a given FOV defined by its x and y coordinates to identify the grid points within the FOV.
        - The maximum value and its corresponding location within the FOV are then determined.
        - The input data array is masked, setting values outside the FOV to NaN.

        Usage Example:
        ```python
        # Assuming 'temperature_data' is a 2D array representing temperature values
        fov_x, fov_y = FOV_area(cam_latitude, cam_longitude, cam_yaw, cam_fov)
        maxlat, maxlon = find_max_in_fov(temperature_data, fov_x, fov_y)
        ```

        Replace 'temperature_data' with the actual 2D array representing your dataset.
        """
        # Define a grid of latitude and longitude within the FOV area
        lons = data.coords['lon'].values
        lats = data.coords['lat'].values
        # Define a grid of latitude and longitude within the FOV area
        polygon_points = list(zip(fov_x, fov_y))
        polygon_path = Path(polygon_points)
        x_grid, y_grid = np.meshgrid(lons, lats)

        # Flatten the grid arrays to 1D arrays
        x_flat = x_grid.flatten()
        y_flat = y_grid.flatten()

        # Create an array of (x, y) points
        points = np.column_stack((x_flat, y_flat))

        # Check if each point is within the polygon
        mask = polygon_path.contains_points(points)

        # Reshape the mask back to 2D
        mask = mask.reshape(x_grid.shape)

        # Apply the mask to your original array
        # Replace original_array with your actual array that you want to mask
        masked_array = data.values.copy()
        masked_array[~mask] = np.nan  # Set values outside the polygon to NaN
        maxlat, maxlon = np.unravel_index(
            np.nanargmax(masked_array), masked_array.shape)

        return maxlat, maxlon

   

    def interp_flag16(self, ds):
        """
        Perform interpolation for flagged data.
        """
        var1 = ds['var1'].copy()
        flag = ds['flag']
        mask = flag == 16
        lon, lat = np.meshgrid(ds['lon'].values, ds['lat'].values)
        points = np.array([lon[~mask], lat[~mask]]).T
        values = var1.values[~mask]
        points_interp = np.array([lon[mask], lat[mask]]).T
        var1_filled = griddata(points, values, points_interp, method='linear')
        ds['var1_filled'] = var1.copy()
        ds['var1_filled'].values[mask] = var1_filled
        return ds

    # Fuction to plot 1km rings from
    def geodesic_point_buffer(self, lat, lon, km):
        # Azimuthal equidistant projection
        proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
        aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
        project = partial(
            pyproj.transform,
            pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
            proj_wgs84)
        buf = Point(0, 0).buffer(km * 1000)  # distance in metres
        return transform(project, buf).exterior.coords.xy

    def plotring(self, data,title):
        """
        Plot a ring around a camera's field of view (FOV) and highlight cloud-related information.

        Parameters:
        - data (xr.DataArray): 2D array of values representing the dataset.
        - ax (matplotlib.axes._subplots.AxesSubplot): Matplotlib axes for plotting.
        - camlat (float): Latitude of the camera's position.
        - camlon (float): Longitude of the camera's position.
        - yaw (float): Yaw angle of the camera in degrees.
        - title (str): Title for the plot.

        Returns:
        - D (float or str): Haversine distance between the camera and the maximum optical depth point, or 'no cloud' if no cloud is found.
        - maxlat_2 (int or str): Index of the latitude with the maximum optical depth within the FOV, or 'none' if no cloud is found.
        - maxlon_2 (int or str): Index of the longitude with the maximum optical depth within the FOV, or 'none' if no cloud is found.

        Note:
        - The function visualizes the FOV, FOV error, and cloud-related information on a plot.
        - It uses a threshold value of 3.6 for cloud detection.
        - The FOV is discretized into 100 points for smoother visualization.
        - The function returns information about the maximum optical depth point within the FOV.

        Usage Example:
        ```python
        # Assuming 'data' is an xarray DataArray representing optical depth values
        # and 'ax' is a Matplotlib axes
        D, maxlat_2, maxlon_2 = plotring(data, ax, camlat, camlon, yaw, "Optical Depth Plot")
        ```

        Replace 'data', 'camlat', 'camlon', 'yaw', and 'title' with your specific values.
        """
        # Load camera details
        yaw_degrees, camlat, camlon = self.load_camera_details()
        fig, ax = plt.subplots(figsize=(20, 20))
        
        mask = data >= 3.6
        masked_data = data.where(mask, other=np.nan)
        masked_data.plot.pcolormesh(x="lon", y="lat", ax=ax, levels=[
                                    3.6, 9.4, 23, 60, 100],
                                    cbar_kwargs={'label': 'optical depth'})
        # Orography file
        orog_file = '/gws/nopw/j04/dcmex/users/dfinney/data/globe_orog_data_NM.nc'
        orog = xr.open_dataset(orog_file)['topo'].sel(
            X=slice(self.lon1, self.lon2), Y=slice(self.lat1, self.lat2))
        southbaldy = [33.99, -107.19]
        MRO = [33.98481699, -107.18926709]
        CB = [34.0248532, -106.9267249]
        clourlist = ['whitesmoke', 'gray', 'khaki', 'steelblue', 'seagreen',
                     'aqua', 'orchid', 'firebrick', 'w', 'k', 'y', 'b', 'g', 'c', 'm', 'r']
        if self.camera == 1:
            distance = [24, 25, 26, 27, 28,   29,  30,
                        31,  32,  33,  34, 35, 36, 37, 38, 39]
        else:   
            distance = [8, 9, 10, 11, 12,   13,  14,
                        15,  16,  17,  18, 19, 20, 21, 23, 24]
        day1 = data.values
        lons = data.coords['lon'].values
        lats = data.coords['lat'].values
        fov_x, fov_y = self.calculate_fov(camlat, camlon, yaw_degrees,self.fov_horizontal_deg)
        # Yaw is plus minus the YAW error
        fov_xp5, fov_yp5 = self.calculate_fov(camlat, camlon, yaw_degrees,self.fov_horizontal_deg + 2*self.yaw_error)

        try:
            test = np.unravel_index(np.nanargmax(day1), day1.shape)
            if test:
                print('cloud found')
        except:
            print('no cloud in area')
            return 

        orog.plot.contour(x="X", y="Y", colors='k', ax=ax,
                        levels=[2400, 2500, 2800, 3300])
        ax.fill(fov_x, fov_y, color='silver', alpha=0.3, label='Field of View')
        ax.fill(fov_xp5, fov_yp5, color='silver',
                alpha=0.2, label='Field of View Error')

        try:
            maxlat_2, maxlon_2 = self.find_max_in_fov(data, fov_xp5, fov_yp5)
            ax.scatter(lons[maxlon_2], lats[maxlat_2], marker='x',
                    color='r', s=400, label='Max optical depth')
            D = hs.haversine((lats[maxlat_2], lons[maxlon_2]), (camlat, camlon))

        except:
            print('no cloud in FOV')
            D = 'no cloud'
            maxlat_2 = 'none'
            maxlon_2 = 'none'
        
        for d, c in zip(distance, clourlist):
            x, y = self.geodesic_point_buffer(camlat, camlon, d)
            ax.plot(x, y, color=c)

        ax.scatter(camlon, camlat, color='r', marker='D', s=400, label='Camera')
        ax.scatter(MRO[1], MRO[0], marker='+', color='k', s=200, label='MRO')
        ax.scatter(CB[1], CB[0], marker='+', color='k', s=150, label='CB')
        ax.scatter(southbaldy[1], southbaldy[0], marker='^',
                color='k', label='South Baldy peak', s=200)
        ax.set_title(title, fontsize='15')
        ax.set_xticks(np.arange(camlon - 1, camlon + 1, 0.1))
        ax.set_yticks(np.arange(camlat - 1, camlat + 1, 0.1))
        ax.set_xlim(self.lon1, self.lon2)
        ax.set_ylim(self.lat1, self.lat2)
        # Add a legend
        if self.camera==1:
            ax.legend(['MRO','CB', '8km', '9km', '10km', '11km', '12km',   '13km',  '14km',
                        '15km',  '16km', '17km',  '18km', '19km', '20km', '21km',
                        '23km', '24km', 'Camera','South Baldy peak'])
        else:   
            ax.legend(['24km', '25km', '26km', '27km', '28km', '29km', '30km',
                       '31km',  '32km',  '33km',  '34km', '35km', '36km', '37km',
                       '38km', '39km','Camera','MRO','CB','South Baldy peak'])
        plt.tight_layout()
        print('Distance to max cloud:', round(D,2), 'km')
        plt.show()
        return D, maxlat_2, maxlon_2

    def process_file(self):
        """
        Process the optical depth satellite data file and generate FOV plots.
        """
        
        file_root = "/gws/nopw/j04/dcmex/data/GOES16pcrgd/Magda/"
        channel1 = "ABI-L2-CODC/"
        fname_root = "/OR_ABI-L2-CODC-M6_G16*_select_pcrgd.nc" 
        # Load satellite data
        date_path = self.date_to_use.replace('-', '/', 3)
        rad = xr.open_mfdataset(glob.glob(file_root + channel1 + date_path + '/'+self.time_to_use[0:2]+fname_root),combine="nested", 
                                 concat_dim="t").sel(lon=slice(self.lon1, self.lon2),
                                                                       lat=slice(self.lat1, self.lat2))
        datetimephoto = datetime.strptime(self.date_to_use+self.time_to_use, "%Y-%m-%d%H%M")
        rad = rad.sel(t=datetimephoto, method='nearest')
        rad = self.interp_flag16(rad)
        # Plot FOV and optical depth data
        self.plotring(rad['var1'], f"Optical Depth Plot for {self.date_to_use}")


def main():
    """
    Main function to be run from the command line.
    """
    if len(sys.argv) < 1:
        print("Usage: python script.py <filename> ")
        sys.exit(1)

    file_name = sys.argv[1]

    processor = CloudOpticalDepthProcessor(file_name)
    processor.process_file()


if __name__ == "__main__":
    main()
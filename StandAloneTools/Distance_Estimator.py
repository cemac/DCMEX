import xarray as xr
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import sys

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

    def __init__(self, file_name, camera):
        """
        Initialize CloudOpticalDepthProcessor with input arguments.
        """
        self.file_name = file_name
        self.storage = '/home/users/hburns/GWS/DCMEX/users/hburns/'
        self.dataroot = '/gws/nopw/j04/dcmex/data'
        self.yaw_error = 10
        self.camera= camera
        self.optical_depth_threshold = 3.6
        self.cam_details_path = f'{self.storage}/camera_details.csv'
        self.cam_df = pd.read_csv(self.cam_details_path)
        

    def extract_file_metadata(self):
        """
        Extract date and time metadata from the file name.
        """
        parts = os.path.splitext(os.path.basename(self.file_name))[0].split('-')
        yyyy, mm, dd, hhmmss = parts[3], parts[4], parts[5], parts[6]
        date_time = datetime.strptime(f'{yyyy}-{mm}-{dd}-{hhmmss}', "%Y-%m-%d-%H%M%S")
        return date_time.strftime("%d-%m-%Y"), date_time.strftime("%Y-%m-%d"), date_time.strftime("%H%M")

    def load_camera_details(self):
        """
        Load camera details for the specific date and camera number.
        """
        date_fnames, _, _ = self.extract_file_metadata()
        filtered_df = self.cam_df[(self.cam_df['Date'] == date_fnames) & (self.cam_df['camera'] == self.camera)]
        yaw_degrees = filtered_df.yaw.values[0]
        camlat = filtered_df.camlat.values[0]
        camlon = filtered_df.camlon.values[0]
        return yaw_degrees, camlat, camlon

    def calculate_fov(self, camlat, camlon, yaw_degrees, fov_horizontal_deg):
        """
        Calculate the coordinates of the Field of View (FOV) area on the map.
        """
        fov_radius = 0.35  # Adjust this for FOV radius
        fov_start = yaw_degrees - fov_horizontal_deg / 2
        fov_end = yaw_degrees + fov_horizontal_deg / 2
        fov_x = [camlon] + [camlon + fov_radius * np.sin(a) for a in np.linspace(np.radians(fov_start), np.radians(fov_end), 100)]
        fov_y = [camlat] + [camlat + fov_radius * np.cos(a) for a in np.linspace(np.radians(fov_start), np.radians(fov_end), 100)]
        return fov_x, fov_y

    def plot_fov(self, data, camlat, camlon, yaw_degrees, title):
        """
        Plot the Field of View (FOV) and cloud-related data.
        """
        mask = data >= self.optical_depth_threshold
        masked_data = data.where(mask, other=np.nan)
        
        fig, ax = plt.subplots(figsize=(20, 20))
        masked_data.plot.pcolormesh(x="lon", y="lat", ax=ax, levels=[3.6, 9.4, 23, 60, 100], cbar_kwargs={'label': 'optical depth'})
        
        fov_x, fov_y = self.calculate_fov(camlat, camlon, yaw_degrees, fov_horizontal_deg=50)
        fov_xp5, fov_yp5 = self.calculate_fov(camlat, camlon, yaw_degrees, fov_horizontal_deg=50 + 2 * self.yaw_error)

        try:
            ax.fill(fov_x, fov_y, color='silver', alpha=0.3, label='Field of View')
            ax.fill(fov_xp5, fov_yp5, color='silver', alpha=0.2, label='Field of View Error')
            ax.scatter(camlon, camlat, color='r', marker='D', s=400, label='Camera')
            ax.set_title(title, fontsize='15')
            ax.legend()
            plt.tight_layout()
            plt.show()
        except:
            print("Error in plotting FOV")

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

    def process_file(self):
        """
        Process the optical depth satellite data file and generate FOV plots.
        """
        # Load camera details
        yaw_degrees, camlat, camlon = self.load_camera_details()

        # Load satellite data
        rad = self.interp_flag16(xr.open_dataset(self.file_name)["var1"])

        # Plot FOV and optical depth data
        self.plot_fov(rad, camlat, camlon, yaw_degrees, f"Optical Depth Plot")


def main():
    """
    Main function to be run from the command line.
    """
    if len(sys.argv) < 2:
        print("Usage: python script.py <filename> <camera_number>")
        sys.exit(1)

    file_name = sys.argv[1]
    camera = int(sys.argv[2])

    processor = CloudOpticalDepthProcessor(file_name, camera)
    processor.process_file()


if __name__ == "__main__":
    main()
import xarray as xr
import glob
import matplotlib.pyplot as plt
from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point

# Set Paramers to read in satelite data regridded into lat lon
lat1 = 33.75
lat2 = 34.25
lon1 = -107.5
lon2 = -106.9
file_root = "/gws/nopw/j04/dcmex/users/dfinney/data/GOES16rgd/Magda/"
channel1 = "ABI-L1b-RadC/"
channel2 = "ABI-L2-ACMC/"
date = "2022/7/31/17"
date2 = "2022/7/25/17"
fname_root = "/OR_ABI-L1b-RadC-M6C01_G16_*_select_rgd.nc"
fname_root2 = "/OR_ABI-*_G16_*_select_rgd.nc"


# List of camera locations from files, dates, corresponding frame, ring colours and distances
camlon = [-106.898107, -106.898355, -106.898280, -106.898235, -106.898220]
camlat = [34.023982, 34.023910, 34.023910, 34.024008, 34.024018]
dates = ['2022-07-25-1704', '2022-07-31-1732',
         '2022-07-31-1733', '2022-07-31-1737', '2022-07-31-1741']
index = [0, 6, 7, 7, 8]
clourlist = ['whitesmoke', 'gray', 'khaki', 'steelblue', 'seagreen', 'aqua', 'orchid', 'firebrick', 'w', 'k', 'y', 'b', 'g', 'c', 'm', 'r']
distance = [24, 25, 26, 27, 28,   29,  30,  31,  32,  33,  34, 35, 36, 37, 38, 39 ]

# Visible radar
rad1 = xr.open_mfdataset(glob.glob(file_root + channel1 + date + fname_root),
                         combine="nested", concat_dim="t")["var1"].sel(lon=slice(lon1, lon2),
                                                                       lat=slice(lat1, lat2))
rad2 = xr.open_mfdataset(glob.glob(file_root + channel1 + date2 + fname_root),
                         combine="nested", concat_dim="t")["var1"].sel(lon=slice(lon1, lon2),
                                                                       lat=slice(lat1, lat2))
data = [rad2, rad1, rad1, rad1]

'''
# ACMC (cloud mask)
cld1 = xr.open_mfdataset(glob.glob(file_root+channel2+date+fname_root2),
                         combine="nested",concat_dim="t")["var1"].sel(lon=slice(lon1,lon2),
                                                                      lat=slice(lat1,lat2))
# more levels
cld2 = xr.open_mfdataset(glob.glob(file_root+channel2+date+fname_root2),
                         combine="nested",concat_dim="t")["var2"].sel(lon=slice(lon1,lon2),
                                                                      lat=slice(lat1,lat2))
# the probability of cloud
cld3 = xr.open_mfdataset(glob.glob(file_root+channel2+date+fname_root2),
                         combine="nested",concat_dim="t")["var3"].sel(lon=slice(lon1,lon2),
                                                                      lat=slice(lat1,lat2))
cld1.plot(col="t",col_wrap=3)
'''


# Fuction to plot 1km rings from
def geodesic_point_buffer(lat, lon, km):
    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres
    return transform(project, buf).exterior.coords.xy

# Plot data, camera and distance rings
def plotring(data, ax, camlat, camlon, title):
    data.plot.pcolormesh(x="lon", y="lat", ax=ax)
    ax.scatter(camlon, camlat, color='r')
    for d, c in zip(distance, clourlist):
        x, y = geodesic_point_buffer(camlat, camlon, d)
        ax.plot(x, y, color=c)
    ax.set_title(title)
    ax.legend(['24km', '25km', '26km', '27km', '28km', '29km', '30km',
               '31km',  '32km',  '33km',  '34km', '35km', '36km', '37km',
               '38km', '39km'])
    return


fig, axs = plt.subplots(2, 2, figsize=(20, 10))
axes_list=[(0,0),(0,1),(1,0),(1,1)]
proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
for i in range(4):
    plotring(data[i][index[i]], axs[axes_list[i]], camlat[i], camlon[i], dates[i])

# https://gis.stackexchange.com/questions/289044/creating-buffer-circle-x-kilometers-from-point-using-python
plt.tight_layout()
plt.show()

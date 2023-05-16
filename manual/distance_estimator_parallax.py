import xarray as xr
import glob
import matplotlib.pyplot as plt
from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point
from GOES import GOES

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


def goes_lonlat_parallax_corrected(goesdataset, heights_ASL):
    # heights_ASL will need to be same grid as goesdataset

    ## haven't got the goes_imager_projection variables in my raw saved data, so going to practice using a sample file for those.
    startime= cth.t[0].values.astype('datetime64[s]').item().strftime('%Y%m%d')
    G = GOES.download('goes16', "ABI-L2-ACHAC", DateTimeIni=startime+'-000000',
                      DateTimeFin=startime+'-230000', domain='C')

    satInfo = G.nearesttime(cth.t[0].values.astype('datetime64[s]').item().strftime('%Y%m%d%-H%M%S'))

    proj_info = satInfo.variables['goes_imager_projection']
    lon_origin = proj_info.attrs["longitude_of_projection_origin"]
    H = proj_info.attrs["perspective_point_height"] +  proj_info.attrs["semi_major_axis"]


    ### dlf18apr2023 adjusting these for the cloud height interpolated to the goesdataset grid
    ## I think this should work. I hope its roughly implementing a similar approach to
    # eq15 in https://www.mdpi.com/2072-4292/12/3/365
    ## probably should be checked
    r_eq = heights_ASL.fillna(0) + proj_info.attrs["semi_major_axis"]
    r_pol = heights_ASL.fillna(0) + proj_info.attrs["semi_minor_axis"]

    # Data info
    lat_rad_1d = goesdataset['x'][:]
    lon_rad_1d = goesdataset['y'][:]

    # create meshgrid filled with radian angles
    lat_rad,lon_rad = np.meshgrid(lat_rad_1d,lon_rad_1d)

    # lat/lon calc routine from satellite radian angle vectors

    lambda_0 = (lon_origin*np.pi)/180.0

    a_var = np.power(np.sin(lat_rad),2.0) + (np.power(np.cos(lat_rad),2.0)*(np.power(np.cos(lon_rad),2.0)+(((r_eq*r_eq)/(r_pol*r_pol))*np.power(np.sin(lon_rad),2.0))))
    b_var = -2.0*H*np.cos(lat_rad)*np.cos(lon_rad)
    c_var = (H**2.0)-(r_eq**2.0)

    r_s = (-1.0*b_var - np.sqrt((b_var**2)-(4.0*a_var*c_var)))/(2.0*a_var)

    s_x = r_s*np.cos(lat_rad)*np.cos(lon_rad)
    s_y = - r_s*np.sin(lat_rad)
    s_z = r_s*np.cos(lat_rad)*np.sin(lon_rad)

    lat = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))*((s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
    lon = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)

    return lon, lat

goes_path = "/gws/nopw/j04/dcmex/data/GOES16/Magda/"
cth = xr.open_mfdataset(goes_path+"ABI-L2-ACHAC/2022/07/19/1[8-9]/*_s20222001[8-9]*_select.nc", combine="nested", concat_dim="t")
cth_lon_original = cth["lon"] ## keep to compare
cth_lat_original = cth["lat"]
cth["lon"], cth["lat"] = goes_lonlat_parallax_corrected(cth.drop(["lat","lon"]).var1, cth.drop(["lat","lon"]).var1)

# List of camera locations from files, dates, corresponding frame, ring colours and distances
camlon = [-106.898107, -106.898355, -106.898280, -106.898235, -106.898220]
camlat = [34.023982, 34.023910, 34.023910, 34.024008, 34.024018]
dates = ['2022-07-25-1704', '2022-07-31-1732',
         '2022-07-31-1733', '2022-07-31-1737', '2022-07-31-1741']
# Index of nearest time: todo: code up nearet time selector
index = [0, 6, 7, 7, 8]
# TODO: create csv of colours and kms to load in
clourlist = ['whitesmoke', 'gray', 'khaki', 'steelblue', 'seagreen',
             'aqua', 'orchid', 'firebrick', 'w', 'k', 'y', 'b', 'g', 'c', 'm', 'r']
distance = [24, 25, 26, 27, 28,   29,  30,
            31,  32,  33,  34, 35, 36, 37, 38, 39]

# Visible radar
rad1 = xr.open_mfdataset(glob.glob(file_root + channel1 + date + fname_root),
                         combine="nested", concat_dim="t")["var1"].sel(lon=slice(lon1, lon2),
                                                                       lat=slice(lat1, lat2))
rad2 = xr.open_mfdataset(glob.glob(file_root + channel1 + date2 + fname_root),
                         combine="nested", concat_dim="t")["var1"].sel(lon=slice(lon1, lon2),
                                                                       lat=slice(lat1, lat2))
data = [rad2, rad1, rad1, rad1, rad1]

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


fig, axs = plt.subplots(3, 2, figsize=(10, 40))
axes_list = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
for i in range(5):
    plotring(data[i][index[i]], axs[axes_list[i]],
             camlat[i], camlon[i], dates[i])

# https://gis.stackexchange.com/questions/289044/creating-buffer-circle-x-kilometers-from-point-using-python
plt.tight_layout()
plt.show()

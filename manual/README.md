# Manual Calculations

* [distance_estimator.py](distance_estimator.py) plots 1km rings on to re-gridded GEOS data (different channels and times/dates available)
* [cloudheightestimator.py](cloudheightestimator.py) Reads [cloud_distance_and_pixel_height.csv](pixel_data/cloud_distance_and_pixel_height.csv) to pass into the height estimator that calculates the height relative to the camera using information about the camera, pixel height and distance to object in frame.


# Input Data

[cloud_distance_and_pixel_height.csv](pixel_data/cloud_distance_and_pixel_height.csv) contains the following information:

* **Time** Date Time to nearest min of image
* **camera** Camera 1 or 2
* **camlat** Latitude from metadata
* **camlon** Longitude from metadata
* **distance_min** min distance in km (nearest km)
* **distance_max** max distance in km (nearest km)
* **CB1** pixel height to Cloud Base 1 (corresponding to CB1 on image)
* **CB2** pixel height to Cloud Base 2 (corresponding to CB2 on image)
* **CB3** pixel height to Cloud Base 3 (corresponding to CB3 on image)
* **CT1** pixel height to Cloud Top 1 (corresponding to CT1 on image)
* **CT2** pixel height to Cloud Top 2 (corresponding to CT2 on image)
* **CT3** pixel height to Cloud Top 3 (corresponding to CT3 on image)

# Results

[cloudheightestimator.py](cloudheightestimator.py) outputs two CSV files:

[cloud_heights_using_max_distance.csv](results/cloud_heights_using_max_distance.csv) & [cloud_heights_using_min_distance.csv](results/cloud_heights_using_min_distance.csv)

These contain the following information

* **Time** Date and time of camera image
* **CBX** Cloud base above sea level (in km)
* **CTX** Cloud top above sea level (in km)

* Cloud Base Height Range: 5.5km -8.5km
* Cloud Top Height Range: 7.02km - 13.11 km

Maximum distances produced much higher cloud heights (~ 1km increase) indicating the need to get better distance estimates.

## To do

1. Plot Camera angle and field of view on the distance plots
2. Calculate 1px error
3. Validation & more test images?
4. Calculate heights of known objects for validation?
5. Produce figures to describe the manual height calculations

# Next steps

If this method looks viable pursue automation:

1. Cloud identification and automated pixel calculation in camera frame
2. Auto cloud detection and distance estimation from GEOS data

This would be feasible in the time frame and work for other data sets.

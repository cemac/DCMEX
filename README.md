<div align="center">
<a href="https://www.cemac.leeds.ac.uk/">
  <img src="https://github.com/cemac/cemac_generic/blob/master/Images/cemac.png"></a>
  <br>
</div>

# DCMEX #


[![GitHub release](https://img.shields.io/github/release/cemac/DCMEX.svg)](https://github.com/cemac/DCMEX/releases) [![GitHub top language](https://img.shields.io/github/languages/top/cemac/DCMEX.svg)](https://github.com/cemac/DCMEX) [![GitHub issues](https://img.shields.io/github/issues/cemac/DCMEX.svg)](https://github.com/cemac/DCMEX/issues) [![GitHub last commit](https://img.shields.io/github/last-commit/cemac/DCMEX.svg)](https://github.com/cemac/DCMEX/commits/master) [![GitHub All Releases](https://img.shields.io/github/downloads/cemac/DCMEX/total.svg)](https://github.com/cemac/DCMEX/releases) ![GitHub](https://img.shields.io/github/license/cemac/DCMEX.svg)


# DCMEX - Automated Measuring of cloud height.

This repository is part of the [Deep Convective Microphysics Experiment (DCMEX)](https://cloudsense.ac.uk/dcmex/) project.

The code here attempts to automatically detect the cloud base and top height from timelapse photography using:

1. Optical cloud depth to estimate distance to max cloud thickness
2. Open CV edge detection to estimate cloud top location in image
3. Thin Lens equations to use lens information, pixel information and distance information to give a pitch corrected cloud top height estimate

All the methodology is outlined in the [DCMEX wiki](https://github.com/cemac/DCMEX/wiki)

# DCMEX - StandAlone Tools.

This repository is part of the [Deep Convective Microphysics Experiment (DCMEX)](https://cloudsense.ac.uk/dcmex/) project.

We also provide standalone tools:

1. `height_calculator.py` 
2. `cloud_boxer.py` given a photo returns a picture with the cloud boxed and pixel number returned
3. `distance_estimator.py` given a photo will return a plot with the corresponding optical depth 

more information on these tools can be found on the [stand alone tools wiki](https://github.com/cemac/DCMEX/wiki/Stand-Alone-Tools)


# Requirements

python requirements are provided in the DCMEX.yml file


# Documentation

Detailed documentation of the the tools and methodology and dataset used is provided in [this repositories wiki](ttps://github.com/cemac/DCMEX/wiki).

# Acknowledgements #

Tool developers: Helen Burns, Declan Finney, Alan Blyth. Data Archiving: Josh Hampton. Data collection:  Finney, D.; Groves, J.; Walker, D.; Dufton, D.; Moore, R.; Bennecke, D.; Kelsey, V.; Reger, R.S.; Nowakowska, K.; Bassford, J.; Blyth, A.

# Licence information #

This code is Licensed under the GPL-3 license

# References

 * Finney, D.; Groves, J.; Walker, D.; Dufton, D.; Moore, R.; Bennecke, D.; Kelsey, V.; Reger, R.S.; Nowakowska, K.; Bassford, J.; Blyth, A. (2023): DCMEX: cloud images from the NCAS Camera 11 from the New Mexico field campaign 2022. NERC EDS Centre for Environmental Data Analysis, 15 December 2023. [doi:10.5285/b839ae53abf94e23b0f61560349ccda1](https://dx.doi.org/10.5285/b839ae53abf94e23b0f61560349ccda1)
*  Finney, D.; Groves, J.; Walker, D.; Dufton, D.; Moore, R.; Bennecke, D.; Kelsey, V.; Reger, R.S.; Nowakowska, K.; Bassford, J.; Blyth, A. (2023): DCMEX: cloud images from the NCAS Camera 12 from the New Mexico field campaign 2022. NERC EDS Centre for Environmental Data Analysis, 15 December 2023. [doi:10.5285/d1c61edc4f554ee09ad370f6b52f82ce](https://dx.doi.org/10.5285/d1c61edc4f554ee09ad370f6b52f82ce)
* Declan Finney, James Groves, Dan Walker, David Dufton, Robert Moore, David Bennecke, Vicki Kelsey, R. Stetson Reger, Kasia Nowakowska, James Bassford, & Alan Blyth. (2023, April 25). Timelapse footage of deep convective clouds in New Mexico produced during the DCMEX field campaign (Version 1). Zenodo. [https://doi.org/10.5281/zenodo.7756710](Declan Finney, James Groves, Dan Walker, David Dufton, Robert Moore, David Bennecke, Vicki Kelsey, R. Stetson Reger, Kasia Nowakowska, James Bassford, & Alan Blyth. (2023, April 25). Timelapse footage of deep convective clouds in New Mexico produced during the DCMEX field campaign (Version 1). Zenodo. https://doi.org/10.5281/zenodo.7756710)
* Finney, D. L. and Blyth, A. M. and Gallagher, M. and Wu, H. and Nott, G. J. and Biggerstaff, M. I. and Sonnenfeld, R. G. and Daily, M. and Walker, D. and Dufton, D. and Bower, K. and B\"oing, S. and Choularton, T. and Crosier, J. and Groves, J. and Field, P. R. and Coe, H. and Murray, B. J. and Lloyd, G. and Marsden, N. A. and Flynn, M. and Hu, K. and Thamban, N. M. and Williams, P. I. and Connolly, P. J. and McQuaid, J. B. and Robinson, J. and Cui, Z. and Burton, R. R. and Carrie, G. and Moore, R. and Abel, S. J. and Tiddeman, D. and Aulich, G (2024):Deep Convective Microphysics Experiment (DCMEX) coordinated aircraft and ground observations: microphysics, aerosol, and dynamics during cumulonimbus development. ESSD-16-2141-2163 [https://essd.copernicus.org/articles/16/2141/2024/](https://essd.copernicus.org/articles/16/2141/2024/)




<div align="center">
<a href="https://www.cemac.leeds.ac.uk/">
  <img src="https://github.com/cemac/DCMEX/blob/master/Images/cemac.png"></a>
  <br>
</div>

# DCMEX #

<!--
[![GitHub release](https://img.shields.io/github/release/cemac/DCMEX.svg)](https://github.com/cemac/DCMEX/releases) [![GitHub top language](https://img.shields.io/github/languages/top/cemac/DCMEX.svg)](https://github.com/cemac/DCMEX) [![GitHub issues](https://img.shields.io/github/issues/cemac/DCMEX.svg)](https://github.com/cemac/DCMEX/issues) [![GitHub last commit](https://img.shields.io/github/last-commit/cemac/DCMEX.svg)](https://github.com/cemac/DCMEX/commits/master) [![GitHub All Releases](https://img.shields.io/github/downloads/cemac/DCMEX/total.svg)](https://github.com/cemac/DCMEX/releases) ![GitHub](https://img.shields.io/github/license/cemac/DCMEX.svg)
-->

# DCMEX - Automated Measuring of cloud height.

This repository is part of the [Deep Convective Microphysics Experiment (DCMEX)](https://cloudsense.ac.uk/dcmex/) project.

The code here attempts to automatically detect the cloud base and top height from timelapse photography using:

1. Optical cloud depth to estimate distance to max cloud thickness
2. Open CV edge detection to estimate cloup top location in image
3. Thin Lens equations to use lens information, pixel information and distance information to give a pitch corrected cloud top height estimate

# Requirements

python requirements are provided in the DCMEX.yml file


# Documentation

Documentation of this work is currently held in the notes directory along with additional documentation in the relevant sub directories

# Acknowledgements #

*coming soon*

# Licence information #

This code is Licensed under the GPL-3 license

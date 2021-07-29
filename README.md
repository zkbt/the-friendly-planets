# the-friendly-planets
Tool for making a cute, neatly aligned, not-to-messy image of a planet one or more moons nearby.

## Installation
If you want to install this code just to use it, you can simply run
```
pip install the-friendly-planets
```

If you want to install this code while being able to edit and develop it, you can fork and/or clone this repository onto your own computer and then install it directly as an editable package by running
```
git clone https://github.com/zkbt/the-friendly-planets.git
cd the-friendly-planets
pip install -e '.[develop]'
```
This will point your environment's `thefriendlyplanets` package to point to this local folder, meaning that any changes you make in the repository will be reflected what Python sees when it tries to `import thefriendlyplanets`. Including the `[develop]` will install both the dependencies for the package itself and the extra dependencies required for development (= testing and documentation).

## Usage

The following snippet of code shows the basic structure and functionality of this code (so far):

```python
from thefriendlyplanets import *
i = make_friendly_image('uranus-test-image.fit')
```

## Contributors

This package was initially developed during the spring 2021 semester of ASTR1030 at the University of Colorado Boulder. The code was primarily written by [Zach Berta-Thompson](https://github.com/zkbt), but the project includes important intellectual contributions from:

- Zach Berta-Thompson
- Michelle Wooten
- Seth Hornstein
- Jackson Avery
- Hope Reynolds
- Melissa Kane
- Rydell Stottlemyer
- Abhishek Kumar
- Charles Danforth
- Daniel Everding

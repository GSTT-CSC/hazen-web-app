Tasks
=================================
The *hazen* application provides automatic quantitative analysis for the following measurements of MRI phantom data:

Signal-to-noise ratio (SNR)
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Provides a map of local SNR across a flood phantom slice. The SNR for each voxel in an image (of a flood phantom) is estimated as the SNR of a ROI centred on that voxel following the single image SNR method of McCann et al.\ :footcite:p:`2013:mcann`

The SNR map can show variation in SNR caused by smoothing filters.

It also highlights small regions of low signal which could be caused by micro-bubbles or foreign bodies in the phantom.

These inhomogeneities can erroneously reduce SNR measurements made by other methods.

Algorithm overview
*******************

#. Apply boxcar smoothing to original image to create smooth image.
#. Create noise image by subtracting smooth image from original image.
#. Create image mask to remove background using e.g. ``skimage.filters.threshold_minimum``.
#. Calculate SNR using McCann's method and overlay ROIs on image.
#. Estimate local noise as standard deviation of pixel values in ROI centred on a pixel. Repeat for each pixel in the noise image.
#. Plot the local noise as a heat map.

SNR(Im) Calculates the SNR for a single-slice image of a uniform MRI phantom.
This script utilises the smoothed subtraction method described in McCann 2013
Created by Neil Heraghty\n\n04/05/2018

Spatial resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Contributors: Haris Shuaib, haris.shuaib@gstt.nhs.uk
Neil Heraghty, neil.heraghty@nhs.net, 16/05/2018
todo:
Replace shape finding functions with hazenlib.tools equivalents

Slice position and width
^^^^^^^^^^^^^^^^^^^^^^^^^^^
`Local Otsu thresholding <https://scikit-image.org/docs/0.11.x/auto_examples/plot_local_otsu.html>`_
Assumptions: Square voxels, no multi-frame support

Uniformity
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Uniformity + Ghosting & Distortion
Calculates uniformity for a single-slice image of a uniform MRI phantom and implements the IPEM/MAGNET method of measuring fractional uniformity.
It also calculates integral uniformity using a 75% area FOV ROI and CoV for the same ROI.
This script also measures Ghosting within a single image of a uniform phantom.
This follows the guidance from ACR for testing their large phantom.
A simple measurement of distortion is also made by comparing the height and width of the circular phantom.
Created by Neil Heraghty
neil.heraghty@nhs.net
14 05 2018

Ghosting
^^^^^^^^^^^^^^^^^^^^^^^^^^^

NEEDS DESCRIPTION

MR Relaxometry
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Measure T1 and T2 in Caliber relaxometry phantom.
Introduction
This module determines the T1 and T2 decay constants for the relaxometry spheres in the Caliber (HPD) system phantom
qmri.com/qmri-solutions/t1-t2-pd-imaging-phantom (plates 4 and 5).
Values are compared to published values (without temperature correction). Graphs of fit and phantom registration images can optionally be produced.

Scan parameters
Manufacturer's details of recommended scan parameters for GE, Philips and\nSiemens scanners are available in the 'System Phantom Manual' which can be downloaded from the above website (T1-VTI and T2 sequences).
However, these may result in long scan times. The parameters below were used to acquire the images used in testing this module. They are provided for information only.

T1 Relaxometry
Sequence: Spin echo with inversion recovery
Plane: Coronal
TR (ms): 1000 (or minimum achievable if longer--see note)
TE (ms): 10\nTI (ms): {50.0, 100.0, 200.0, 400.0, 600.0, 800.0}
Flip angle: 180 degrees
Matrix: 192 x 192
FoV (mm): 250 x 250
Slices: 2 (or 3 to acquire plate 3 with PD spheres)
Slice width (mm): 5
Distance factor: 35 mm / 700%
NSA: 1
Receive bandwidth:
GE (kHz): 15.63
Philips (Hz / px): 109
Siemens (Hz / px): 130

Reconstruction: Normalised

Note: Some scanners may require a longer TR for long TI values.
This algorithm will accommodate a variation in TR with TI and incomplete recovery due to short TR.
T2 Relaxometry
Sequence:
GE: T2 map (TE values fixed)
Other manufacturers: Spin echo multi contrast
Plane: Coronal
TR (ms): 2000
Number of contrasts: maximum
TE (ms): minimum
Flip angle: 90 degrees
Matrix: 192 x 192
FoV (mm): 250 x 250
Slices: 2 (or 3 to acquire plate 3 with PD spheres)
Slice width (mm): 5
Distance factor: 35 mm / 700%
NSA: 1
Receive bandwidth:
GE (kHz): 15.63
Philips (Hz / px): 109
Siemens (Hz / px): 130
Reconstruction: Normalised

Algorithm overview
1. Create ``T1ImageStack`` or ``T2ImageStack`` object which stores a listof individual DICOM files (as ``pydicom`` objects) in the ``.images`` attribute.
2. Obtain the RT (rotation / translation) matrix to register the template image to the test image. Four template images are provided, one for each relaxation parameter (T1 or T2) on plates 4 and 5, and regression is performed on the first image in the sequence. Optionally output the overlay image to visually check the fit.
3. An ROI is generated for each target sphere using stored coordinates, the RT transformation above, and a structuring element (default is a 5x5 boxcar).
4. Store pixel data for each ROI, at various times, in an ``ROITimeSeries`` object. A list of these objects is stored in ``ImageStack.ROI_time_series``.
5. Generate the fit function. For T1 this looks up TR for the given TI (using piecewise linear interpolation if required) and determines if a magnitude or signed image is used. No customisation is required for T2 measurements.
6. Determine relaxation time (T1 or T2) by fitting the decay equation to the ROI data for each sphere. The published values of the relaxation times are used to seed the optimisation algorithm. For T2 fitting the input data are truncated for TE > 5*T2 to avoid fitting Rician noise in magnitude images with low signal intensity. Optionally plot and save the decay curves.
7. Return plate number, relaxation type (T1 or T2), measured relaxation times, published relaxation times, and fractional differences in a dictionary.

Feature enhancements
Template fit on bolt holes--possibly better with large rotation angles -have bolthole template, find 3 positions in template and image, figure out transformation.

Template fit on outline image--poss run though edge detection algorithms then fit.

Use normalised structuring element in ROITimeSeries. This will allow correct calculation of mean if elements are not 0 or 1.

Get r-squared measure of fit.

Tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Exceptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^
 Application-specific errors

MR Relaxometry
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Logger
^^^^^^^

References
~~~~~~~~~~~
.. footbibliography::
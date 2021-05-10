#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
This module is to build Red Relief Images Map (RRIM) from a DEM.

This is a python implementation of Chiba T., Kaneta S. & Suzuki Y. (2008), 
Red Relief Image map: New visualisation for three dimensional data, ISPRS.

Please, if you use this module, cite :
Robert X., pyRRIM, a python RRIM Implementation, 2021; Zenodo : 

# Copyright (c) 2021 Xavier Robert <xavier.robert@ird.fr>
# SPDX-License-Identifier: GPL-3.0-or-later


INPUTS:
    demname (string)            : Path and name of the DEM to use for RRIM process
                                  This has been tested with tif and geotiff files with succes
    nodatavalue (int, optional) : Value used to describe No Data
                                  Defaults to -9999
    demfill (bool, optional)    : True to impose the filling of the depressions
                                  False to avoid the fill of the depressions
                                  Defaults to False
    svf_n_dir (int, optional)   : number of directions for openness
                                  See the RVT_py documentation for more info
                                  Default to 8
    svf_r_max (int, optional)   : max search radius in pixels for openness
                                  See the RVT_py documentation for more info
                                  Default to 10
    svf_noise (int, optional)   : level of noise remove for openness
                                  0-don't remove, 1-low, 2-med, 3-high
                                  See the RVT_py documentation for more info
                                  Default to 0
    saturation (int, optional)  : manages the red saturation (from slope)
                                  Used to build the HSV color scale
                                  Default to 90
    brithness (int, optional)   : the brithness (from diff. openness)
                                  Used to build the HSV color scale
                                  Default to 150
    isave (bool, optional)      : True to save temporary rasters (slope, openness,...)
                                  False to avoid saving temporary rasters
                                  Defaults to True
    ikeep (bool, optional)      : True to use existing slope and openness rasters
                                  False to recompute slope and openness rasters
                                  This is usefull when we just play with colors parameters!
                                  Defaults to False

OUTPUT:
    RRIM raster as a geotiff file. 
    If the original image is georeferenced, the RRIM will also be georeferenced 
    in the same projection system ad geographical reference

USAGE:
    To generate a RRIM geotiff from the DEM ./Test/test.tif, 
    that contains no data values as -9999 and with a depression filling,
    after installation of the module, run in a python interpreter:
        >>> from pyRRIM import rrim
        >>> rrim(demname = '../Test/test.tif', nodatavalue = -9999, demfill = True,
            svf_n_dir = 8, svf_r_max = 20, svf_noise = 0,
            saturation = 80, brithness = 40,
            isave = True, ikeep = False)
    
    If you do not install as a module, you can also, use the present file as a script file.
    Just, copy the script file in the folder you want to work, 
    then, modify the parameters in the function main (last function of the file),
    and finaly run in a terminal window (where is your script file!):
        ~$ python pyRRIM.py

INSTALL:
    In the top folder, run in your terminal:
    ~$ python setup.py install
    
    or use pip:
    pip install pyRRIM
"""
import cv2
import numpy as np
import richdem as rd
from osgeo import gdal
import rvt.vis
import time, os
from alive_progress import alive_bar              # https://github.com/rsalmei/alive-progress

####################################################
####################################################
def colorScheme(size):
    """
    Function to compute color scheme from HSV to RGB
    Function from Xin Yao : https://github.com/susurrant/

    Args:
        size (tupple of integers): (a, b, c); a gives the saturation, b the brithness
                                   and c correspond to the number of bands of the image; this is set to 3

    Returns:
        RRIM_map (x * y * 3 uint8 array) : RGB array
    """
    
    img_hsv = np.zeros(size, dtype=np.uint8)

    # saturation
    saturation_values = np.linspace(0, 255, size[0])
    for i in range(0, size[0]):
        img_hsv[i, :, 1] = np.ones(size[1], dtype=np.uint8) * np.uint8(saturation_values[i])

    # value
    V_values = np.linspace(0, 255, size[1])
    for i in range(0, size[1]):
        img_hsv[:, i, 2] = np.ones(size[0], dtype=np.uint8) * np.uint8(V_values[i])

    return cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)


####################################################
def saveImage(output_fname, result, raster):
    """
    Function to save an array to a geotiff file

    Args:
        output_fname (string)                   : Name of the new raster yo write in geotiff format
        result (array of uint8, 3 bands)        : Array of 3 bands uint8 
                                                  (values from 0 to 255, for RGB coding)
        raster (GDAL/richDEM-type raster object): Raster that have been used to generate the new raster
                                                  to save in geotiff;
                                                  used to extract the original geographic data 
                                                  to clip to the new raster
    """
    
    cv2.imwrite(output_fname, result)

    print('\tWritting %s...' % output_fname)

    # Transform tiff image to geotiff image with the same geo-data than the original and slope rasters
    out=gdal.Open(output_fname, gdal.GA_Update)
    out.SetGeoTransform(raster.geotransform)
    out.SetProjection(raster.projection)
    out = None 

    return

####################################################
def checkfiles(rasterfnme):
    """
    Function to test if a file exists and if it is readable:
        If yes, it returns a True boolean
        If not, it returns a False boolean
    
    Args:
        rasterfnme (string) : path and name of the file to check
    
    Returns:
        israter (Boolean) : True if the file exists and is readable
                            False if not!
    """	
        
    israster = False
    # Check if the DEM exists
    if os.path.isfile(rasterfnme) and os.access(rasterfnme, os.R_OK):
        # if raster exists
        israster = True
        
    return israster

####################################################
def genRRIMImage(slopedata, openness, color_size, output_fname):
    """
    Function to generate rrim image using the Slope matrix and the differential openness matrix

    Args:
        slopedata (array)    : Numpy or Richdem array that corresponds 
                               to the slope raster
        openness (array)     : Numpy or Richdem array that corresponds 
                               to the differential opennsess raster
        color_size (tupple)  : tupple of integers (a, b, c); 
                               a gives the saturation, b the britness
        output_fname (string): Name of the RRIM raster file (geotiff)
    """

    # build the color map/scheme
    RRIM_map = colorScheme(color_size)

    result = np.zeros((slopedata.shape[0], slopedata.shape[1], 3), dtype = np.uint8)

    # Define the progress-bar
    with alive_bar(3, title = "\x1b[32;1m- Processing RRIM final\x1b[0m", length = 35) as bar:
        # Compute the color given by the slope
        inc = np.uint8(abs(slopedata))
        inc[inc > (color_size[0]-1)] = color_size[0] - 1
        # Update the progress-bar
        bar()

        # Compute the grey given by the openness
        #openness_val = np.uint8(openness + color_size[1] / 2)
        openness_val = np.uint8((openness + color_size[1]) / 2)
        openness_val[openness_val < 0] = 0
        openness_val[openness_val >= color_size[1]] = color_size[1] - 1
        # Update the progress-bar
        bar()

        # build the RGB tuples
        result = RRIM_map[inc, openness_val]
        # Update the progress-bar
        bar()

    # sav image as geotiff
    saveImage(output_fname, result, slopedata)

    return


####################################################
def timer(func):
    def wrapper(*args, **kw):
        """
        Function to Compute time cost
        """
        startTime = time.time()
        callback =  func(*args, **kw)
        print('\n\033[96mTotal running time:\033[00m \033[91m%.3f' % ((time.time() - startTime) / 60.0), 'mins\033[00m')
        return callback
    return wrapper

####################################################
def factorz(DEM):
    """
    Function to compute the z factor in function of the latitude
    Needed to compute the slope, and the openness if the DEM is in Lat-Long

    Args:
        DEM (rd array): Digital Elevation Model

    Returns:
        zfactor (Float): z factor correction
    """

    if 'degree' in DEM.projection and not 'PROJECTION' in DEM.projection:
       zfactor = 1 / (111320 * np.cos(abs(DEM.geotransform[3])*np.pi/180))
    else: 
       zfactor = 1

    return zfactor


####################################################
def openness(DEM, slopeMat, svf_n_dir = 8, svf_noise = 0, svf_r_max = 20,
             demname = None, nodatavalue = None, isave = True):
    """
    Function to compute the positive, negative and differential openness

    Args:
        DEM (rd array)               : Digital elevation model
        slopeMat (np array)          : Slope array computed from the digital elevation model
        svf_n_dir (int, optional)    : number of directions for openness
                                       Default to 8
        svf_r_max (int, optional)    : max search radius in pixels for openness
                                       Default to 10
        svf_noise (int, optional)    : level of noise remove for openness
                                       0-don't remove, 1-low, 2-med, 3-high
                                       Default to 0
        nodatavalue (float, optional): No data values
                                       Defaults to None; because otherwise, it crashes???
        isave (bool, optional)       : True to save the positive, negative and differential
                                       openness rasters as geotiffs files
                                       False otherwise
                                       Defaults to True

    Returns:
        opennessMat (np array of DEM.shape): Differential openness array
    """

    # Define the progress-bar
    with alive_bar(3, title = "\x1b[32;1m- Processing Openness\x1b[0m", length = 37) as bar:
        # Function to compute the positive openness
        dict_svf = rvt.vis.sky_view_factor(dem = DEM, resolution = abs(DEM.geotransform[1]),
        #dict_svf = rvt.vis.sky_view_factor_compute(height_arr = DEM, 
                                       compute_svf = False, compute_asvf = False, compute_opns = True,
                                       svf_n_dir = svf_n_dir, svf_r_max = svf_r_max, svf_noise = svf_noise,
                                       no_data = nodatavalue, 
                                       #no_data = None, 
                                       fill_no_data = False, keep_original_no_data = False)
        pos_opns_arr = dict_svf["opns"]  # positive openness
        # Update the bar at each step
        bar()

        # Fonction to compute the negative openness
        DEM_neg_opns = DEM * -1  # dem * -1 for neg opns
        # we don't need to calculate svf and asvf (compute_svf=False, compute_asvf=False)
        dict_svf = rvt.vis.sky_view_factor(dem = DEM_neg_opns, resolution = abs(DEM.geotransform[1]), 
        #dict_svf = rvt.vis.sky_view_factor_compute(height_arr = DEM_neg_opns,
                                       compute_svf = False, compute_asvf = False, compute_opns = True,
                                       svf_n_dir = svf_n_dir, svf_r_max = svf_r_max, svf_noise = svf_noise,
                                       no_data = nodatavalue,
                                       #no_data = None, 
                                       fill_no_data = False, keep_original_no_data = False)
        neg_opns_arr = dict_svf["opns"] #- 90 # negative openness
        # Update the bar at each step
        bar()

        # Compute the differential openness
        opennessMat = (pos_opns_arr - neg_opns_arr) / 2

        # Update the bar at each step
        bar()

    if isave:
        saveImage(demname[:-4]+'_pos_opns.tif', pos_opns_arr, slopeMat)
        saveImage(demname[:-4]+'_neg_opns.tif', neg_opns_arr, slopeMat)
        saveImage(demname[:-4]+'_diff_opns.tif', opennessMat, slopeMat)

        return opennessMat


####################################################
@timer
def rrim(demname, nodatavalue = -9999, demfill = False,
         svf_n_dir = 8, svf_r_max = 10, svf_noise = 0,
         saturation = 90, brithness = 150,
         isave = True, ikeep = False):
    """
    RRIM function
        This is the one to call to compute a RRIM image from a DEM.

    Args:
        demname (string)            : path and name of the DEM to use for RRIM process
        nodatavalue (int, optional) : Value used to describe No Data
                                      Defaults to -9999
        demfill (bool, optional)    : True to impose the filling of the depressions
                                      False to avoid the fill of the depressions
                                      Defaults to False
        svf_n_dir (int, optional)   : number of directions for openness
                                      Default to 8
        svf_r_max (int, optional)   : max search radius in pixels for openness
                                      Default to 10
        svf_noise (int, optional)   : level of noise remove for openness
                                      0-don't remove, 1-low, 2-med, 3-high
                                      Default to 0
        saturation (int, optional)  : manages the red saturation (from slope)
                                      Used to build the HSV color scale
                                      Default to 90
        brithness (int, optional)   : the brithness (from diff. openness)
                                      Used to build the HSV color scale
                                      Default to 150
        isave (bool, optional)      : True to save temporary rasters (slope, openness,...)
                                      False to avoid saving temporary rasters
                                      Defaults to True
        ikeep (bool, optional)      : True to use existing slope and openness rasters
                                      False to recompute slope and openness rasters
                                      This is usefull when we just play with colors parameters!
                                      Defaults to False
    """

    # If the minima input data are not given print the help file
    if demname == None or not demname: help(rrim)

    print('##################################################\n')
    print('              RRIM computation\n')
    print('##################################################\n')
    # 1- check/build the working structure
    # update the name of the output file name
    rrimFile = demname[:-4]+'_rrim.tif'  # output file name

    # build the color triplet used to build the HSV color scale using the saturation and brithness
    color_size=(saturation, brithness, 3)

    # 2- Read the DEM
    if checkfiles(demname):
        # If the DEM exists in the declared folder, load it
        DEM = rd.LoadGDAL(demname, no_data = nodatavalue)
    else:
        # If not, insult the user...
        raise NameError(u'\033[91mERROR:\033[00m F** input raster %s DEM does not exist' % demname)

    print('\x1b[32;1m- Working with :\033[00m')
    print('\tDEM file     :', demname)
    print('\tshape        :', DEM.shape)
    print('\tz range      : %d - %d' % (np.min(np.array(DEM)), np.max(np.array(DEM))))
    print('\tcell size (m):', DEM.geotransform[1] / factorz(DEM))
    print('\tsearch radius: %s px / %s m ' % (svf_r_max, svf_r_max * DEM.geotransform[1] / factorz(DEM)))
    
    print('\n\033[96mBe patient, it could be long...\033[00m \033[91mGrab a beer !\033[00m\n')

    # 3- Process DEM (Fill depression...) with richDEM if needed
    if checkfiles(demname[:-4]+'_slope.tif') and checkfiles(demname[:-4]+'_diff_opns.tif') and ikeep:
        print('Slope and Differential openness raster exists...\nI am reading data from them')
        slopeMat = rd.LoadGDAL(demname[:-4]+'_slope.tif', no_data = nodatavalue)
        opennessMat = rd.LoadGDAL(demname[:-4]+'_diff_opns.tif', no_data = nodatavalue)
        # 4- Prosses the RRIM
        print('\nstart rrim...\n')
    else:
        if demfill:
            print('\x1b[32;1m- Filling Depressions...\x1b[0m')
            DEM = rd.FillDepressions(DEM, epsilon = False, in_place = False)
        else:
            print('\x1b[32;1mNO Fill Depressions\x1b[0m')
        # 4- Prosses the RRIM
        print('\nstart rrim...\n')

        # 4.1 Compute slope map, using a zfactor if needed
        with alive_bar(1, title = "\x1b[32;1m- Processing Slope\x1b[0m", length = 40) as bar:
            # Richdem slope computation if need to change
            #slopeMat = rd.TerrainAttribute(DEM, 
            #                               attrib = 'slope_degrees',
            #                               zscale = factorz(DEM))
            # RVT_py slope computation
            dict_slope_aspect = rvt.vis.slope_aspect(dem = DEM, 
                                         resolution_x = abs(DEM.geotransform[1]), 
                                         resolution_y = abs(DEM.geotransform[5]),
                                         output_units = "degree", 
                                         ve_factor = factorz(DEM), 
                                         #no_data=nodatavalue, # problem with dem[dem == no_data] = np.nan
                                         no_data = None,
                                         fill_no_data = False, keep_original_no_data = False)
            slopeMat = dict_slope_aspect["slope"]
            bar()
        if isave:
            saveImage(demname[:-4]+'_slope.tif', slopeMat, slopeMat)

        # 4.2 openness step
        opennessMat = openness(DEM, slopeMat, svf_n_dir, svf_noise, svf_r_max, 
                               demname, nodatavalue, isave)

        # If the calculated raster looks very pixelized, we might resample the grey value matrix 
        # with a bilinear or cubic method
        # TO DO

    # 4.3 img generation step
    genRRIMImage(slopeMat, opennessMat, color_size, rrimFile)

    print('\nrrim complete.')

    return

#############################################################################
if __name__ == '__main__':
    
    # Define parameters
    demname = '../Test/test.tif'
    nodatavalue = -9999
    demfill = True
    isave = True
    ikeep = False
    #color_size=(90, 50, 3) # Slightly red
    #color_size=(60, 50, 3) # Quite red
    saturation = 80
    brithness = 40

    # Set the parameters for raster computations
    svf_n_dir = 8  # number of directions (for openness)
    svf_r_max = 20  # max search radius in pixels (for openness)
    svf_noise = 0  # level of noise remove (0-don't remove, 1-low, 2-med, 3-high) (for openness)

    # Call the function
    rrim(demname, 
         nodatavalue = nodatavalue, 
         demfill = demfill,
         svf_n_dir = svf_n_dir,
         svf_r_max = svf_r_max,
         svf_noise = svf_noise,
         saturation = saturation,
         brithness = brithness,
         isave = isave, ikeep = ikeep)
    
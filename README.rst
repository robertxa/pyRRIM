pyRRIM
========

This code is to built **Red Relief Image Maps (RRIM)** from a raster (DEM). It is a python implementation of *Chiba T., Kaneta S. & Suzuki Y. (2008), Red Relief Image map: New visualisation for three dimensional data, ISPRS*.

If the input image is a georeference image, the RRIM produced will also be georeferenced in the same system and projection.

This module is rapid, but may contain numerous ``bugs``, and could probably be ameliorate and/or optimized. If you have any comments, do not hesitate to add a new branch or to contact the author.

To know the ``history``, please check the file History.txt

Run as a script file
--------------------

If you have a ponctual use of this module, you are not obliged to install it as a module. You can use the present file **pyRRIM/pyRRIM.py** as a ``script file``. But you still need to unstall the depedencies of the script! (See further)

1. Just, copy the script file in the folder you want to work, 

2. then, modify the parameters in the function main (last function of the file),

3. and finaly run in a terminal window (where is your script file!):
        
.. code-block:: bash
			
	python pyRRIM.py

Install
-------

This folder has been prepared as a classic python module that you can install as usual.

To install it:

.. code-block:: bash

	pip install pyRRIM

or, inside the master folder:

.. code-block:: bash
	
	python setup.py install

To update it:

.. code-block:: bash

	pip install -U pyRRIM

If during the update you get a problem with the update of a dependency, you may try:

.. code-block:: bash

	pip install -U --no-deps pyRRIM

The module has been written and tested with Python 3.9, but not tested with Python 2.7.

Dependencies
------------

This code needs the following python modules and their dependencies, you may install them before the installation of the **pyRRIM** module:
	- cv2
	- richdem
	- alive_progress
	- numpy
	- osgeo/gdal
	- time
	- rvt_py

Usage
-----

Inside a (i)python environnement:

To import the module:

.. code-block:: python

	>>> from pyRRIM import rrim
	
To produce a RRIM image from the raster 'Test/dem.tif' (wich contains no data values as -9999):

.. code-block:: python

    >>> rrim(demname = '../Test/test.tif', nodatavalue = -9999, demfill = True, svf_n_dir = 8, svf_r_max = 20, svf_noise = 0, saturation = 80, brithness = 40, isave = True, ikeep = False)

To use it as a simple script module, see the previous **Run as a script file** section.

Options/inputs
--------------

To use options or inputs, you need to set them as	

.. code-block:: python

    >>> rrim(option_name = option_value, [...])
	
Options/inputs are (option_names):

1. ``demname`` (string): name of the raster to work with for RRIM process. This has been tested with tif and geotiff files with succes.
				
	Add the full path to the raster. Personally, I like to store my rasters in a DEM/folder		
					
	ex: ``rasterfnme = 'Dem/Dem_Fusion-Peru_projUTM.tif'``
					
	Default = ``None``
	
2. ``nodatavalue`` (int, optional): Value used to describe No Data in the input raster

				ex: ``nodatavalue = -9999``

				Default: ``nodatavalue = -9999``

3. ``demfill`` (bool, optional): True to impose the filling of the depressions, False to avoid the fill of the depressions
                                
								ex:  ``demfill = True``

								Default: ``demfill = False``

4. ``svf_n_dir`` (int, optional): number of directions for openness: 8 is usually sufficient. See the RVT_py documentation for more info.
                                
								ex: ``svf_n_dir = 16``

								Default: ``svf_n_dir = 8``

5. ``svf_r_max`` (int, optional): max search radius in pixels for openness. See the RVT_py documentation for more info.
                                
								Ex: ``svf_r_max = 20```

								Default: ``svf_r_max = 10``

6. ``svf_noise`` (int, optional): level of noise remove for openness; 0-don't remove, 1-low, 2-med, 3-high. See the RVT_py documentation for more info.

								ex: ``svf_noise = 2``
                                
								Default: ``svf_noise = 0``

7. ``saturation`` (int, optional): manages the red saturation (from slope). This is used to build the HSV color scale. You may need to play with this value to get a correct colorized RRIM.
                                
								Ex: ``saturation = 50``

								Default: ``saturation = 90``

8. ``brithness`` (int, optional): manages the brithness (from diff. openness). This is used to build the HSV color scale. You may need to play with this value to get a correct exposed RRIM.
                                
								Ex: ``brithness = 90``

								Default: ``brithness = 150``

9. ``isave`` (bool, optional): True to save temporary rasters (slope, openness,...), or False to avoid saving temporary rasters
                            	
								Ex: ``isave = False``
								
								Default: ``isave = True``

10. ``ikeep`` (bool, optional): True to use existing slope and openness rasters, or False to recompute slope and openness rasters. This is usefull when we just play with colors parameters!
                                
								Ex: ``ikeep = True``
								
								Default: ``ikeep = False``

Help files
----------

To get help in your (i)python environnement:

.. code-block:: python

	>>> help(pyRRIM)

Examples
--------

To generate a RRIM geotif from the DEM ./Test/test.tif, that contains no data values as -9999 and with a depression filling, after installation of the module, run in a (i)python interpreter:

.. code-block:: python

>>> from pyRRIM import rrim
>>> rrim(demname = '../Test/test.tif', nodatavalue = -9999, demfill = True, svf_n_dir = 8, svf_r_max = 20, svf_noise = 0, saturation = 80, brithness = 40, isave = True, ikeep = False)

The previous line permits to build the RRIM image with the use of the DEM located in the Test/ folder:

.. image:: https://github.com/robertxa/pyRRIM/blob/main/Test/test_rrim.png
   :scale: 100 %
   :align: center
			
Outputs
-------

The output is a single raster file that is a 3-bands RRIM Image. It is stored as a geotiff file.
If asked (parameter ``isave`` set to True), slope raster and positive, negative and, differential openness rasters are also svaed as geotiff files.

How to cite
-----------

Please, if you use this module, cite :
**Robert X., pyRRIM, a python RRIM Implementation (2021), DOI:10.5281/Zenodo.4745556**

.. image:: https://zenodo.org/badge/365968726.svg
   :target: https://zenodo.org/badge/latestdoi/365968726

Contact
-------

If needed, do not hesitate to add a new branch or to contact the author. 
Please, use `https://www.isterre.fr/identite_id135055.html# <https://www.isterre.fr/identite_id135055.html#>`_

Licence
-------

Copyright (c) 2021 Xavier Robert <xavier.robert@ird.fr>
SPDX-License-Identifier: GPL-3.0-or-later


######!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
#from importlib.metadata import version

# Import of the lib pyRRIM
import pyRRIM

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='pyRRIM',
	version=pyRRIM.__version__,
	description='package that provides tools to build RRIM from a raster map',
	long_descritpion=open('README.rst').read(),
	url='https://github.com/robertxa/pyRRIM',
	download_url='https://github.com/robertxa/pyRRIM/archive/master.zip',
	author='Xavier Robert',
	author_email='xavier.robert@ird.fr',
	license='GPL-V3.0',
	packages=find_packages(),
	#include_package_data=True,	# What is the use of it ?
	install_requires=[
	      'opencv-python',
	      'richdem',
	      'numpy',
	      'alive_progress',
	      'gdal',
		  'rvt_py'
	],
	classifiers=[
		"Operating System :: OS Independent",
		"Topic :: Scientific/Engineering :: GIS"
	],
	include_package_data=True,
	zip_safe=False)
      
######!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021 Xavier Robert <xavier.robert@ird.fr>
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import  division
# This to be sure that the result of the division of 2 integers is a real, not an integer
from __future__ import absolute_import
from __future__ import print_function

__version__ = '1.0.4'

# Import modules
import sys, os, time
#import copy
import numpy as np
import cv2
import richdem as rd
from osgeo import gdal
import rvt.vis
from alive_progress import alive_bar

# Import all the functions

from .pyRRIM import *

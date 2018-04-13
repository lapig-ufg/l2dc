import re
import os
import gdal
import osr
import subprocess
from tools import gdal_utils

gdal.UseExceptions();

def lxAnglesImage(mtlFile, stackedFile, outputFile):
	
	command = ["fmask_usgsLandsatMakeAnglesImage.py",]
	command += ['-m', mtlFile]
	command += ['-t', stackedFile]
	command += ['-o', outputFile]

	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def lxSaturationImage(mtlFile, stackedFile, outputFile):
	
	command = ["fmask_usgsLandsatSaturationMask.py",]
	command += ['-m', mtlFile]
	command += ['-i', stackedFile]
	command += ['-o', outputFile]

	#print(" ".join(command))
	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def lxTOA(mtlFile, stackedFile, angleFile, outputFile):
	
	command = ["fmask_usgsLandsatTOA.py",]
	command += ['-i', stackedFile]
	command += ['-m', mtlFile]
	command += ['-z', angleFile]
	command += ['-o', outputFile]

	#print(" ".join(command))
	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def lxFmask(mtlFile, toaStackedImgs, thermalStackedImgs, angleFile, saturationImage, outputFile):
	
	command = ["fmask_usgsLandsatStacked.py",]
	
	command += ['-t', thermalStackedImgs]
	command += ['-a', toaStackedImgs]
	command += ['-m', mtlFile]
	command += ['-z', angleFile]
	command += ['-s', saturationImage]
	command += ['-o', outputFile]

	#print(" ".join(command))
	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def s2AnglesImage(xmlFile, outputFile):
	
	command = ["fmask_sentinel2makeAnglesImage.py",]
	command += ['-i', xmlFile]
	command += ['-o', outputFile]

	#print(" ".join(command))
	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def s2Fmask(stackedImgs, angleFile, outputFile):

	command = ["fmask_sentinel2Stacked.py",]
	
	command += ['-a', stackedImgs]
	command += ['-z', angleFile]
	command += ['-o', outputFile]

	#print(" ".join(command))
	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
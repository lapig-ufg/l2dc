import os
import utils
import subprocess
from . import gdal_utils

def registration(configFile, orthoPath = 'ortho'):

	command = [orthoPath, '-r', configFile]

	print(" ".join(command))

	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def generateConfig(baseLandsatImage, baseWarpImage, outputDir, warpImages, configFilepath, fillValue=0, resampleMethod='NN', baseLandsatImageInfo = None):

	if baseLandsatImageInfo is None:
		baseLandsatImageInfo = gdal_utils.info(baseLandsatImage);
	
	outputImages = []
	warpDataType = []
	warpImagesAux = []

	for warpImage in warpImages:
		
		outputImages.append(os.path.join(outputDir, utils.basename(warpImage,'img')));
		warpImageInfo = gdal_utils.info(warpImage);
		warpImagesAux.append(warpImage);

		if warpImageInfo['dataType'] == 'BYTE':
			warpDataType.append('1');
		else:
			warpDataType.append('2');

	warpImagesList = ",".join(warpImagesAux);

	outputBaseImage = os.path.join(outputDir, utils.basename(baseWarpImage))
	outputImagesList = ",".join(outputImages);
	warpDataTypeList = ' '.join(warpDataType)

	content ="PARAMETER_FILE \n" + \
 	"\n" + \
	"BASE_FILE_TYPE = GEOTIFF\n" + \
	"BASE_LANDSAT = " + baseLandsatImage + "\n" + \
	"UTM_ZONE = -22\n" + \
	"BASE_SATELLITE = Landsat7\n" + \
 	"\n" + \
	"WARP_FILE_TYPE = GEOTIFF\n" + \
	"WARP_SATELLITE = MySensor\n" + \
	"WARP_NBANDS = " + str(len(warpImagesAux)) + "\n" + \
	"WARP_LANDSAT_BAND = " + warpImagesList + "\n" + \
	"WARP_BAND_DATA_TYPE = " + warpDataTypeList + "\n" + \
	"WARP_BASE_MATCH_BAND = " + baseWarpImage + "\n" + \
 	"\n" + \
	"OUT_PIXEL_SIZE = " + str(baseLandsatImageInfo['pixelWidth']) + "\n" + \
	"RESAMPLE_METHOD = " + resampleMethod + "\n" + \
	"OUT_EXTENT = BASE\n" + \
	"BK_VALUE = "+ str(fillValue) +"\n" + \
	"OUT_LANDSAT_BAND = " + outputImagesList + "\n" + \
	"OUT_BASE_MATCH_BAND = " + outputBaseImage + "\n" + \
	"OUT_BASE_POLY_ORDER = 1\n" + \
 	"\n" + \
	"END";

	configFile = open(configFilepath, "w")
	configFile.write(content)
	configFile.close()

	return outputImages
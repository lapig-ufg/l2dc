import utils
import os
from _module import Module
from tools import gdal_utils
from tools import fmask_utils

class Cloud(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module Cloud')

		images = message.get('images');
		sensor = message.get('sensor');
		outputDir = os.path.join(self.module_path,sensor['id'])
		utils.createDir(outputDir);

		if sensor['id'] in ['L8_OLI_T1','L7_ETM_T1']:
				toa = message.get('toa');
				if toa is not None:
					
					bqaFile = None;
					for image in images:
						if image['type'] == 'METADATA':
							bqaFile = image['filepath'];
							break;

					metadataFile = toa['mtl_filepath']
					filepathNobandNoExt = toa['noband_noext_filepath'];

					toaImages = toa['toa_filepath_imgs']
					thermalImages = toa['thermal_filepath_imgs']

					stackedFile = toa['dn_stacked_filepath'];
					toaStackedFile = os.path.join(outputDir, filepathNobandNoExt + 'toa.vrt');
					thermalStackedFile = os.path.join(outputDir, filepathNobandNoExt + 'themal.vrt');
					
					anglesFile = toa['angles_filepath'];
					saturationFile = os.path.join(outputDir, filepathNobandNoExt + 'saturation.tif');

					fmaskImage = os.path.join(outputDir, filepathNobandNoExt + '_fmask.tif');
					cloudImage = os.path.join(outputDir, filepathNobandNoExt + z'cloud.tif');
					
					if not utils.fileExist(toaStackedFile):
						gdal_utils.vrtStack(toaImages,toaStackedFile);
					
					if not utils.fileExist(thermalStackedFile):
						gdal_utils.vrtStack(thermalImages,thermalStackedFile);

					if not utils.fileExist(saturationFile):
						fmask_utils.lxSaturationImage(metadataFile, stackedFile, saturationFile)

					if not utils.fileExist(fmaskImage):
						fmask_utils.lxFmask(metadataFile, toaStackedFile, thermalStackedFile, anglesFile, saturationFile, fmaskImage)

					if not utils.fileExist(cloudImage):
						
						#bqaFilter = 'logical_or({1}<672, {1}>680)'
						bqaFilter = '{1} == 672'
						if sensor['id'] == 'L8_OLI_T1':
							bqaFilter = '{1} == 2720'
							#bqaFilter = 'logical_or({1}<2720, {1}>2728)'

						gdal_utils.calc([fmaskImage,bqaFile],cloudImage,"logical_or(logical_and({0}>=2, {0}<=3),"+bqaFilter+")",'Byte',0);
import utils
import os
from _module import Module
from tools import gdal_utils
from tools import fmask_utils

class Toa(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module Toa')
		images = message.get('images');

		thermalImages = [];
		spectralImages = [];

		if images[0]['sensor_id'] in ['L8_OLI_T1','L7_ETM_T1']:
			
			metadataFile = None;
			filepathNobandNoExt = None;

			outputDir = os.path.join(self.module_path,images[0]['sensor_id'])
			outputFiles = []
			utils.createDir(outputDir);

			for image in images:
				filepathNobandNoExt = image['filename_noband_noext']
				metadataFile = image['filepath_metadata']
				if image['is_thermal_band'] == 1:
					thermalImages.append(image['filepath']);
				else:
					spectralImages.append(image['filepath']);
					outputFiles.append( os.path.join(outputDir, image['filename']) );

			stackedFile = os.path.join(outputDir, filepathNobandNoExt + '.vrt');
			anglesFile = os.path.join(outputDir, filepathNobandNoExt + 'angle.tif');
			toaFile = os.path.join(outputDir, filepathNobandNoExt + 'toa.tif');

			gdal_utils.vrtStack(spectralImages,stackedFile);
			
			if not utils.fileExist(anglesFile):
				fmask_utils.lxAnglesImage(metadataFile, stackedFile, anglesFile)

			if not utils.fileExist(toaFile):
				fmask_utils.lxTOA(metadataFile, stackedFile, anglesFile, toaFile)

			print(utils.fileExist(outputFiles[0]), outputFiles[0])
			if not utils.fileExist(outputFiles[0]):
				gdal_utils.destack(toaFile,outputFiles);
				utils.removeFileIfExist(toaFile);
			
			for outputFile in outputFiles:
				image['fileinfo'] = gdal_utils.info(outputFile)
				image['filepath'] = outputFile

			message.set('toa', { "angles_filepath": anglesFile })

		self.publish(message);
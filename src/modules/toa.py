import utils
import os
from ._module import Module
from tools import gdal_utils
from tools import fmask_utils

class Toa(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module Toa')
		
		images = message.get('images');
		sensor = message.get('sensor');

		thermalImages = [];
		spectralImages = [];

		if sensor['id'] in ['L8_OLI_T1','L7_ETM_T1']:
			
			metadataFile = None;
			filepathNobandNoExt = None;

			outputDir = os.path.join(self.module_path,sensor['id'])
			outputFiles = []
			utils.createDir(outputDir);

			for image in images:
				
				filepathNobandNoExt = image['filename_noband_noext']
				metadataFile = image['filepath_metadata']

				if image['type'] == 'THERMAL':
					thermalImages.append(image['filepath']);
				elif image['type'] == 'SPECTRAL':
					spectralImages.append(image['filepath']);
					outputFiles.append( os.path.join(outputDir, image['filename']) );

			stackedFile = os.path.join(outputDir, filepathNobandNoExt + '.vrt');
			anglesFile = os.path.join(outputDir, filepathNobandNoExt + 'angle.tif');
			toaFile = os.path.join(outputDir, filepathNobandNoExt + 'toa.tif');

			if not utils.fileExist(stackedFile):
				gdal_utils.vrtStack(spectralImages,stackedFile);
			
			if not utils.fileExist(anglesFile):
				fmask_utils.lxAnglesImage(metadataFile, stackedFile, anglesFile)

			if not utils.fileExist(toaFile):
				if self.debug_flag == 1:
					utils.log(self.name, 'Creating ', toaFile)
				fmask_utils.lxTOA(metadataFile, stackedFile, anglesFile, toaFile)
			elif self.debug_flag == 1:
				utils.log(self.name, toaFile, ' already exists.')


			if not utils.fileExist(outputFiles[0]):
				gdal_utils.destack(toaFile,outputFiles);
				utils.removeFileIfExist(toaFile);
			
			for image in images:
				for outputFile in outputFiles:
					if image['filename'] == utils.basename(outputFile):
						image['fileinfo'] = gdal_utils.info(outputFile)
						image['filepath'] = outputFile

			message.set('toa', { 
				"noband_noext_filepath": filepathNobandNoExt,
				"angles_filepath": anglesFile,
				"mtl_filepath": metadataFile,
				"thermal_filepath_imgs": thermalImages,
				"toa_filepath_imgs": outputFiles,
				"dn_stacked_filepath": stackedFile
			})

		self.publish(message);
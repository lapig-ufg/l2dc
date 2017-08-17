import utils
import os
from _module import Module
from tools import arop_utils
from tools import gdal_utils

class Arop(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module')
		images = message.get('images');

		outputDir = os.path.join(self.module_path, images[0]['sensor_id']);

		redImage, nirImage, baseWarpImage = self.separateImages(images)

		if(redImage is not None and nirImage is not None):
			if redImage['sensor_id'] not in ['L8_OLI_T1','L7_ETM_T1']:
					
					ndviFilepath = os.path.join(outputDir, utils.newBasename(redImage['filename'], '_NDVI'));
					baseNdviLandsat = os.path.join(self.ref_wrs_dir,'NDVI_'+redImage['wrs']['id']+".tif");
					
					utils.createDir(outputDir);

					self.processNdvi(redImage, nirImage, ndviFilepath)
					self.processArop(baseNdviLandsat, ndviFilepath, outputDir, baseWarpImage, redImage)

			else:
				self.createImageSymLinks(images, outputDir);

			for image in images:
				outputFile = os.path.join(outputDir, image['filename']);
				
				if not gdal_utils.isValid(outputFile):
					return
				
				image['fileinfo'] = gdal_utils.info(outputFile);
				image['filepath'] = outputFile;

			self.publish(message);

		else:
			utils.log(self.name, images[0]['filename'], ' - RED or NIR bands doesn\'t exists.')

	def processArop(self, baseNdviLandsat, ndviFilepath, outputDir, baseWarpImage, redImage):
		aropRedFile = os.path.join(outputDir,redImage['filename']);
		
		if not utils.fileExist(aropRedFile):
			configFilepath = arop_utils.generateConfig(baseNdviLandsat, ndviFilepath, outputDir, baseWarpImage);
			arop_utils.registration(configFilepath, self.arop_path)

		elif self.debug_flag == 1:
			utils.log(self.name, aropRedFile, ' and other arop files already exists.');

	def processNdvi(self, redImage, nirImage, ndviFilepath):
		
		if not utils.fileExist(ndviFilepath):
			ndviInput = [redImage['filepath'], nirImage['filepath']];
			expression = '({1}.astype(float) - {0}.astype(float))/({1}.astype(float) + {0}.astype(float))*100'
			gdal_utils.calc(ndviInput, ndviFilepath, expression, 'Byte', -1)

		elif self.debug_flag == 1:
			utils.log(self.name, ndviFilepath, ' already exists.')

	def separateImages(self, images):
		redImage = None
		nirImage = None
		baseWarpImage = []

		for image in images:
			if (image['is_red_band']):
				redImage = image;
			elif (image['is_nir_band']):
				nirImage = image;

			baseWarpImage.append(image['filepath']);

		return redImage, nirImage, baseWarpImage;

	def createImageSymLinks(self, images, outputDir):
		for image in images:
			
			outputFile = os.path.join(outputDir,image['filename']);
			inputFile = image['filepath']

			utils.createDir(outputDir);

			if not utils.fileExist(outputFile):
				utils.createSynLink(inputFile, outputFile);

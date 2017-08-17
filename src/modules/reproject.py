import utils
import os
from tools import gdal_utils
from _module import Module

class Reproject(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module')
		images = message.get('images');

		for image in images:
			
			outputDir = os.path.join(self.module_path,image['sensor_id'])
			outputFile = os.path.join(outputDir, utils.basename(image['filename'], 'tif'));
			inputFile = image['filepath']

			utils.createDir(outputDir);

			if(image['fileinfo']['format'] != 'GeoTIFF' or image['fileinfo']['srid'] != image['wrs']['utm_srid']):
				
				if not utils.fileExist(outputFile):
					gdal_utils.reproject(inputFile, outputFile, image['wrs']['utm_srid'])
				elif self.debug_flag == 1:
					utils.log(self.name, outputFile, ' already exists.')

				image['fileinfo'] = gdal_utils.info(outputFile)
				image['filepath'] = outputFile
				image['filename'] = utils.basename(image['filename'], 'tif')
				
			else:
				if not utils.fileExist(outputFile):
					utils.createSynLink(inputFile, outputFile);

			image['filepath'] = outputFile

		self.publish(message);
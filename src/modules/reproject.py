import utils
import os
from tools import gdal_utils
from ._module import Module

class Reproject(Module):

	def __init__(self, config):
		Module.__init__(self, config)

		self.defaultNodataValue = -32765
		self.defaultDataType = 'Int16'

	def process(self, message):
		utils.log(self.id(), 'Executing module')
		images = message.get('images');
		sensor = message.get('sensor')

		outputDir = os.path.join(self.module_path,sensor['id'])
		utils.createDir(outputDir);

		for image in images:
			
			outputFile = os.path.join(outputDir, utils.basename(image['filename'], 'tif'));
			inputFile = image['filepath']

			if not gdal_utils.isValid(outputFile):
				if self.debug_flag == 1:
					utils.log(self.id(), 'Creating ', outputFile)
				
				srid = image['wrs']['utm_srid']
				srcNodata = image['nodata_value']
				
				gdal_utils.reproject(inputFile, outputFile, srid, srcNodata, self.defaultNodataValue, self.defaultDataType)

			elif self.debug_flag == 1:
				utils.log(self.id(), outputFile, ' already exists.')

			try:
				image['filepath'] = outputFile
				image['fileinfo'] = gdal_utils.info(outputFile)
				image['filename'] = utils.basename(image['filename'], 'tif')
		
				image['nodata_value'] = self.defaultNodataValue
				
			except Exception as e:
				utils.removeFile(outputFile)
				utils.log(self.id(), 'Invalid file ', outputFile)

		message.set('tmpFilepaths', [])

		self.publish(message);
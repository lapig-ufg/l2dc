import utils
import os
from ._module import Module
from tools import gdal_utils

class Indexes(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module Ndvi')
		
		sensor = message.get('sensor')
		images = message.get('images');

		outputDir = os.path.join(self.module_path,sensor['id'])
		utils.createDir(outputDir)

		redImage, nirImage = self.separateImages(images)

		if(redImage is not None and nirImage is not None):

			ndviIndex = self.ndvi(redImage, nirImage, outputDir)
			ndviByteIndex = self.ndviByte(redImage, nirImage, outputDir)
			indexesArray = [ndviIndex, ndviByteIndex]

			message.set('images', self.createImagesDict(redImage, indexesArray) )

			self.publish(message);
			
		else:
			utils.log(self.id(), images[0]['filename'], ' - RED or NIR bands doesn\'t exists.')


	def separateImages(self, images):
		redImage = None
		nirImage = None

		for image in images:
			if (image['is_red_band']):
				redImage = image;
			elif (image['is_nir_band']):
				nirImage = image;

		return redImage, nirImage;

	def ndviByte(self, redImage, nirImage, outputDir):
		
		ndviFilepath = os.path.join(outputDir, utils.newBasename(redImage['filename'], '_BNDVI'));

		if not utils.fileExist(ndviFilepath):
			if self.debug_flag == 1:
				utils.log(self.id(), 'Creating ', ndviFilepath)
			ndviInput = [redImage['filepath'], nirImage['filepath']];
			expression = '({1}.astype(float) - {0}.astype(float))/({1}.astype(float) + {0}.astype(float))*100'
			gdal_utils.calc(ndviInput, ndviFilepath, expression, 'Byte', -1, 'GTiff')

		elif self.debug_flag == 1:
			utils.log(self.id(), ndviFilepath, ' already exists.')

		return {'name': 'NDVI_Byte', 'filepath': ndviFilepath }

	def ndvi(self, redImage, nirImage, outputDir):
		
		ndviFilepath = os.path.join(outputDir, utils.newBasename(redImage['filename'], '_NDVI'));

		if not utils.fileExist(ndviFilepath):
			if self.debug_flag == 1:
				utils.log(self.id(), 'Creating ', ndviFilepath)
			ndviInput = [redImage['filepath'], nirImage['filepath']];
			expression = '({1}.astype(float) - {0}.astype(float))/({1}.astype(float) + {0}.astype(float))*10000'
			gdal_utils.calc(ndviInput, ndviFilepath, expression, 'Int16', redImage['nodata_value'], 'GTiff')

		elif self.debug_flag == 1:
			utils.log(self.id(), ndviFilepath, ' already exists.')

		return {'name': 'NDVI', 'filepath': ndviFilepath }

	def createImagesDict(self, baseImage, indexesArray):
		
		result = []

		for index in indexesArray:
			indexImage = {}
			
			indexImage['name'] = index['name']
			indexImage['filename'] = utils.basename(index['filepath'])
			indexImage['filepath'] = index['filepath']
			indexImage['filename_noband_noext'] = utils.basenameNoExt(index['filepath'])
			indexImage['original_spatial_resolution'] = baseImage['spatial_resolution']
			
			indexImage['wrs'] = baseImage['wrs']
			indexImage['type'] = baseImage['type']
			indexImage['sensor_id'] = baseImage['sensor_id']
			indexImage['overpass_id'] = baseImage['overpass_id']
			indexImage['nodata_value'] = baseImage['nodata_value']
			indexImage['aquisition_date'] = baseImage['aquisition_date']
			indexImage['filepath_metadata'] = baseImage['filepath_metadata']

			result.append(indexImage)

		return result

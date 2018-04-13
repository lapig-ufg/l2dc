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

		#if message.hasKey('cloud_mask') and len(images) > 0:
		#	cloudMaskReprojected = self.reprojectCloudMask(images[0], message.get('cloud_mask'), outputDir)
		#	message.set('cloud_mask', cloudMaskReprojected)

		for image in images:
			
			outputFile = os.path.join(outputDir, utils.basename(image['filename'], 'tif'));
			inputFile = image['filepath']

			# Erdas Imagine Images (.img)
			#if(image['fileinfo']['format'] != 'GeoTIFF' or image['fileinfo']['srid'] != image['wrs']['utm_srid']):
				
			#file_is_valid = False
			#while(not file_is_valid):
			if not utils.fileExist(outputFile):
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
				#file_is_valid = True
			except Exception as e:
				utils.removeFile(outputFile)
				utils.log(self.name, 'Invalid file ', outputFile)
					#file_is_valid = False

		self.publish(message);
			#else:
			#	if not utils.fileExist(outputFile):
			#		utils.createSynLink(inputFile, outputFile);

	#def reprojectCloudMask(self, baseImage, cloudMask, outputDir):
		
	#	srid = baseImage['wrs']['utm_srid']
	#	srcNodata = baseImage['nodata_value']
		
	#	cloudMaskReprojected = os.path.join(outputDir, utils.basename(cloudMask))
		
	#	gdal_utils.reproject(cloudMask, cloudMaskReprojected, srid, srcNodata, self.defaultNodataValue, self.defaultDataType)

	#	return cloudMaskReprojected
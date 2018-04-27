import utils
import os
from ._module import Module
from tools import arop_utils
from tools import gdal_utils

class Arop(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.id(), 'Executing module')
		
		images = message.get('images');
		sensor = message.get('sensor');
		tmpFilepaths = message.get('tmpFilepaths');

		outputDir = os.path.join(self.module_path, images[0]['sensor_id']);
		utils.createDir(outputDir);
		
		ndviImage, baseWarpImages = self.separateImages(images)
		
		cloudMaskAroped = None
		if message.hasKey('cloud_mask'):
			tmpFilepaths.append(message.get('cloud_mask'))
			baseWarpImages.append(message.get('cloud_mask'))
			cloudMaskAroped = os.path.join(outputDir, utils.basename(message.get('cloud_mask')))

		if(ndviImage is not None and len(baseWarpImages) > 0):
			
			ndviFilepath = ndviImage['filepath'];
			configFilepath = os.path.join(outputDir,utils.basename(ndviFilepath, 'conf'))

			if not utils.fileExist(configFilepath):
				baseNdviLandsat = os.path.join(self.ref_wrs_dir,'NDVI_'+ndviImage['wrs']['id']+".tif");

				if sensor['id'] == 'L8_OLI_T1' or sensor['id'] == 'L7_ETM_T1' or sensor['id'] == 'L5_TM_T1':
					self.adjustBounds(baseNdviLandsat, baseWarpImages, outputDir)
				else:
					resampleMethod = 'NN'
					if images[0]['original_spatial_resolution'] <= 30:
						resampleMethod = 'AGG'

					fillValue = images[0]['nodata_value']
					self.processArop(baseNdviLandsat, ndviFilepath, outputDir, baseWarpImages, ndviImage, configFilepath, fillValue, resampleMethod)

			elif self.debug_flag == 1:
				utils.log(self.id(), configFilepath, ' and other arop files already exists.');

			aropImages = []

			for image in images:
				
				tmpFilepaths.append(image['filepath'])
				outputFile = os.path.join(outputDir, image['filename']);

				if gdal_utils.isValid(outputFile):
					
					if not gdal_utils.isValid(outputFile):
						utils.log(self.id(), 'Invalid file ', outputFile)
						return
					
					image['fileinfo'] = gdal_utils.info(outputFile);
					image['filepath'] = outputFile;

					aropImages.append(image)

			if gdal_utils.isValid(cloudMaskAroped):
				message.set('cloud_mask', cloudMaskAroped)
				
			message.set('images', aropImages)
			message.set('tmpFilepaths', tmpFilepaths)

			if len(aropImages) > 0:
				self.publish(message);

		else:
			utils.log(self.id(), images[0]['filename'], ' - NDVI index don\'t exists.')

	def adjustBounds(self, baseNdviLandsat, baseWarpImages, outputDir):
		for imageFilepath in baseWarpImages:
			outputFile = os.path.join(outputDir, utils.basename(imageFilepath));
			gdal_utils.fitToBounds(imageFilepath, baseNdviLandsat, outputFile)

	def processArop(self, baseNdviLandsat, ndviFilepath, outputDir, baseWarpImages, baseImage, configFilepath, fillValue, resampleMethod):

		outputImages = arop_utils.generateConfig(baseNdviLandsat, ndviFilepath, outputDir, baseWarpImages, 
																		configFilepath, fillValue, resampleMethod)

		if self.debug_flag == 1:
			utils.log(self.id(), 'Co-regiter using ', configFilepath)
			
		arop_utils.registration(configFilepath, self.arop_path)

		for i in range(0, len(outputImages)):
			binaryFile = outputImages[i]
			geotiffFile = utils.newFilepathExtension(binaryFile, '.img', '.tif')

			if gdal_utils.isValid(binaryFile):
				gdal_utils.convertToGeotiff(binaryFile, geotiffFile)

				utils.removeFile(binaryFile)
				utils.removeFile(binaryFile+'.hdr')

	def separateImages(self, images):
		ndviImage = None
		baseWarpImages = []

		for image in images:
			if (image['name'] == 'NDVI_Byte'):
				ndviImage = image;
			else:
				baseWarpImages.append(image['filepath']);

		return ndviImage, baseWarpImages;

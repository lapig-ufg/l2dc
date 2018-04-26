import utils
import os
from ._module import Module
from tools import gdal_utils
from tools import cloud_utils
from tools import fmask_utils

class Cloud(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def getOutputFile(self, outputDir, filenameNobandNoExt):
		return os.path.join(outputDir, filenameNobandNoExt + 'CLOUD_MASK' + '.tif')

	def getInputImages(self, images, cloudBandNumber, shadowBandNumber):
		cloudInputImage = None
		shadowInputImage = None

		for image in images:
			if (image['band_number'] == cloudBandNumber):
				cloudInputImage = image
			elif (image['band_number'] == shadowBandNumber):
				shadowInputImage = image

		return cloudInputImage, shadowInputImage

	def bqa(self, images, cloudScreening, outputDir):
		cloudInputImage, _ = self.getInputImages(images, cloudScreening['cloud_input_band'], None)
		cloudInputFile = cloudInputImage['filepath']

		outputFile = self.getOutputFile(outputDir, cloudInputImage['filename_noband_noext'])
		cloudValTh = cloudScreening['cloud_val_threshold']
		nodataValue = cloudInputImage['nodata_value']

		if not utils.fileExist(outputFile):
			if self.debug_flag == 1:
				utils.log(self.name, 'Creating ', outputFile)
			gdal_utils.calc([cloudInputFile], outputFile, "{0} != "+str(cloudValTh), 'Int16', nodataValue)
		elif self.debug_flag == 1:
			utils.log(self.name, outputFile, ' already exists.')

		return outputFile

	def fmask(self, sensor, images, outputDir):
		if sensor['id'] in ['2A_MSI']:

			spectralImages = []

			nodataValue = None
			for image in sorted(images, key=lambda img: img['band_number']):
				
				filepathNobandNoExt = image['filename_noband_noext']
				metadataFile = image['filepath_metadata']
				spectralImages.append(image['filepath'])
				nodataValue = image['nodata_value']

			stackedFile = os.path.join(outputDir, filepathNobandNoExt + '.vrt')
			anglesFile = os.path.join(outputDir, filepathNobandNoExt + 'angle.tif')
			
			outputFile = self.getOutputFile(outputDir, filepathNobandNoExt)
			fmaskOutput = outputFile.replace('.tif','.img')
			outputFileFullResolution = outputFile.replace('.tif','full.tif')

			if not utils.fileExist(stackedFile):
				gdal_utils.vrtStack(spectralImages, stackedFile)

			if not utils.fileExist(anglesFile):
				fmask_utils.s2AnglesImage(metadataFile, anglesFile)

			if not utils.fileExist(outputFile):
				if self.debug_flag == 1:
					utils.log(self.name, 'Creating ', outputFile)
				
				fmask_utils.s2Fmask(stackedFile, anglesFile, fmaskOutput)

				expression = "logical_and({0}>=2, {0}<=3)"
				gdal_utils.calc([fmaskOutput], outputFileFullResolution, expression, 'Int16', nodataValue)
				gdal_utils.resample(outputFileFullResolution, outputFile, 10) # BUGFUX: hardcode resolution
				utils.removeFile(fmaskOutput)
				utils.removeFile(outputFileFullResolution)

			elif self.debug_flag == 1:
				utils.log(self.name, outputFile, ' already exists.')

			return outputFile

	def radSlice(self, images, cloudScreening, outputDir):
		cloudRadTh = cloudScreening['cloud_val_threshold']
		shadowRadTh = cloudScreening['shadow_val_threshold']

		cloudInputImage, shadowInputImage = self.getInputImages(images, cloudScreening['cloud_input_band'], cloudScreening['shadow_input_band'])

		if cloudInputImage is not None:
			cloudInputFile = cloudInputImage['filepath']
			shadowInputFile = shadowInputImage['filepath']
			meanSolarAzimuth = cloudInputImage['wrs']['mean_solar_azimuth']
			meanSolarZenith = cloudInputImage['wrs']['mean_solar_zenith']
			nodataValue = cloudInputImage['nodata_value']

			outputFile = self.getOutputFile(outputDir, cloudInputImage['filename_noband_noext'])

			if not utils.fileExist(outputFile):
				if self.debug_flag == 1:
					utils.log(self.name, 'Creating ', outputFile)
				cloud_utils.rad_slice(cloudInputFile, shadowInputFile, outputFile, cloudRadTh, shadowRadTh, meanSolarZenith, meanSolarAzimuth, nodataValue)
			elif self.debug_flag == 1:
				utils.log(self.name, outputFile, ' already exists.')

			return outputFile
		else:
			return None

	def process(self, message):
		utils.log(self.name, 'Executing module Cloud')

		images = message.get('images')
		sensor = message.get('sensor')
		cloudScreening = message.get('cloud_screening')

		outputDir = os.path.join(self.module_path,sensor['id'])
		utils.createDir(outputDir)

		approach = cloudScreening['approach']

		if approach is not None:

			outputFile = None
			if (approach == 'RAD_SLICE'):
				outputFile = self.radSlice(images, cloudScreening, outputDir)
			elif (approach == 'BQA'):
				outputFile = self.bqa(images, cloudScreening, outputDir)
			elif (approach == 'FMASK'):
				outputFile = self.fmask(sensor, images, outputDir)

			if gdal_utils.isValid(outputFile):
				message.set('cloud_mask',outputFile)
				self.publish(message)
			else:
				utils.log(self.name, 'Invalid file ', outputFile)
		
		else:
			self.publish(message)
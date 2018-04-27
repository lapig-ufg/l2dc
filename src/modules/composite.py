import os
import gdal
import utils
import numpy as np
from scipy import stats

from ._module import Module
from tools import gdal_utils

class Composite(Module):

	def __init__(self, config):
		Module.__init__(self, config)

		self.sensorValues = {
				'L8_OLI_T1': 1
			,	'L7_ETM_T1': 2
			,	'L5_TM_T1': 3
			,	'C4_MUX': 4
			,	'CB_HRCC': 5
			,	'C2_HRCC': 6
			,	'R2_LISS3': 7
			,	'R1_LISS3': 8
			,	'UK_SLIM6': 9
			,	'TR_ASTER': 10
			,	'2A_MSI': 11
			,	'PV_VEG': 12
			,	'TR_MOD': 13
			,	'SP_VIIRS': 14
		}

		self.nodataValue = -32765
		self.backgroudSensorId = 'TR_MOD'
		self.referenceSensors = ['L8_OLI_T1', 'L5_TM_T1', 'L7_ETM_T1', 'PV_VEG', 'TR_MOD']

		self.minFillPixelsPercentage = 1

	def getCompositeBasepath(self, outputDir, compositeParams):
		return 	os.path.join(outputDir, "_".join([ 
															compositeParams['spectral_index'], compositeParams['wrs']['id'],
															compositeParams['start_date'], compositeParams['end_date'] 
														]) 
													)

	def sensorPrioritization(self, images):
		
		sensors = {}
		for sensor in images:

			if sensor in self.referenceSensors:
				for index in range(0, len(self.referenceSensors)):
					if sensor == self.referenceSensors[index]:
						sensors[sensor] = index		

			else:
				sensors[sensor] = images[sensor][0]['original_spatial_resolution']
		
		return sorted(sensors, key=sensors.__getitem__)

	def separateImage(self, images):

		referenceImage = None
		fillImages = {}

		for refSensor in self.referenceSensors:
			if refSensor in images:
				referenceImage, referenceImageIndex = self.bestImage(images[refSensor])
				images[refSensor].pop(referenceImageIndex)
				break

		#print(refSensor, referenceImage)
		if len(images[refSensor]) is 0:
			del images[refSensor]

		if self.debug_flag == 1:
			utils.log(self.id(), 'Reference image: ', referenceImage['img_filepath'])

		return referenceImage, images

	def bestImage(self, images):

		bestImage = None
		bestImageIndex = None

		for i in range(0, len(images)):
			if bestImage is None:
				bestImage = images[i]
				bestImageIndex = i
			elif abs(images[i]['center_interval_distance']) < abs(bestImage['center_interval_distance']):
				bestImage = images[i]
				bestImageIndex = i

		return bestImage, bestImageIndex

	def fillTheGaps(self, referenceImage, fillImages, compositeBasepath):
	
		referenceDs, referenceData = gdal_utils.readImage(referenceImage['img_filepath'])
		_, referenceGaps = gdal_utils.readImage(referenceImage['cloud_filepath'])

		referenceSpatialResolution = referenceImage['original_spatial_resolution']
		sensoMetadata, doyMetadata, qaMetadata = self.emptyMetadata(referenceImage, referenceData)
		
		referenceGapsTotalCount = np.sum(np.logical_and((referenceGaps == 1), (referenceGaps != self.nodataValue)))

		for image in self.imagesPrioritization(referenceData, referenceGaps, referenceSpatialResolution, fillImages):
			referenceGapIndexes = np.logical_and((referenceGaps == 1), (referenceGaps != self.nodataValue))
			referenceGapsPercentage = self.getGapsPercentage(referenceGaps)

			if (referenceGapsPercentage == 0.0):
				break

			_, imageData = gdal_utils.readImage(image['img_filepath'])
			_, imageGaps = gdal_utils.readImage(image['cloud_filepath'])

			dataMap = (imageData != self.nodataValue)
			if image['sensor_id'] != self.backgroudSensorId:
				dataMap = np.logical_and( np.logical_and((imageGaps == 0), (imageData != self.nodataValue)), dataMap)
			
			fillMap = np.logical_and(referenceGapIndexes, dataMap)

			fillPixelCount = (fillMap[fillMap]).shape[0]
			fillPixelPercentage = (fillPixelCount / referenceGapsTotalCount) * 100

			print(fillPixelPercentage)
			if fillPixelPercentage <= self.minFillPixelsPercentage:
				continue;

			if self.debug_flag == 1:				
				utils.log(self.id(), 'Fill image:', image['img_filepath'])
				utils.log(self.id(), 'R2 value:', str(image['r2Value']))
				utils.log(self.id(), 'Approach:', str(fillPixelCount), "pixels", "("+str(round(fillPixelPercentage,4)) +"%", "reference gaps)")
				utils.log(self.id(), 'Reference Gaps:', str(round(referenceGapsPercentage,2))+"%")

			if image['r2Value'] == 0:
				fillData = image['intercept'] + imageData[fillMap]*image['slope']
			else:
				fillData = imageData[fillMap]

			referenceData[fillMap] = fillData
			referenceGaps[fillMap] = 0

			doyMetadata[fillMap] = image['acquisition_doy']
			sensoMetadata[fillMap] = self.sensorValues[image['sensor_id']]
			qaMetadata[fillMap] = int(image['r2Value'] * 100)
		
		if self.debug_flag == 1:
			utils.log(self.id(), 'Creating images data and metadata')

		gdal_utils.writeImage(compositeBasepath + '.tif', referenceData, referenceDs)
		gdal_utils.writeImage(compositeBasepath + '_sensors.tif', sensoMetadata, referenceDs, gdal.GDT_Byte)
		gdal_utils.writeImage(compositeBasepath + '_qa.tif', qaMetadata, referenceDs, gdal.GDT_Byte)
		gdal_utils.writeImage(compositeBasepath + '_doy.tif', doyMetadata, referenceDs)

	def emptyMetadata(self, referenceImage, referenceData):
		
		sensoMetadata = np.zeros_like(referenceData)
		sensoMetadata = np.where(referenceData != self.nodataValue, self.sensorValues[referenceImage['sensor_id']], 255)
		
		doyMetadata = np.zeros_like(referenceData)
		doyMetadata = np.where(referenceData != self.nodataValue, referenceImage['acquisition_doy'], 255)

		qaMetadata = np.zeros_like(referenceData)
		qaMetadata = np.where(referenceData != self.nodataValue, 100, 255)

		return sensoMetadata, doyMetadata, qaMetadata

	def getGapsPercentage(self, image):
		
		validImage = (image != self.nodataValue)
		validImageXsize, validImageYSize = validImage.shape

		onlyGaps = np.logical_and((image == 1), (image != self.nodataValue))

		return (np.sum(onlyGaps) / (validImageXsize * validImageXsize) * 100)

	def imagesPrioritization(self, referenceData, referenceGaps, referenceSpatialResolution, images):

		def byCenterIntevalDistance(element):
			return element['r2Value']

		betterSpatialResolution = []
		worseSpatialResolution = []
		
		for sensor in images:

			if self.debug_flag == 1:
				utils.log(self.id(), 'Radiometric normalization for', sensor, 'images')

			for image in images[sensor]:
				_, imageData = gdal_utils.readImage(image['img_filepath'])
				_, imageGaps = gdal_utils.readImage(image['cloud_filepath'])
				
				intercept, slope, r2Value = self.radiometricNormalization(referenceData, referenceGaps, imageData, imageGaps)
				image['slope'] = slope
				image['r2Value'] = r2Value
				image['intercept'] = intercept

			imageSpatialResolution = images[sensor][0]['original_spatial_resolution']
			if referenceSpatialResolution >= imageSpatialResolution:
				betterSpatialResolution += images[sensor]
			else:
				worseSpatialResolution += images[sensor]
		
		betterSpatialResolution = sorted(betterSpatialResolution, key=byCenterIntevalDistance, reverse=True)
		worseSpatialResolution = sorted(worseSpatialResolution, key=byCenterIntevalDistance, reverse=True)
		
		result = betterSpatialResolution + worseSpatialResolution

		return result

	def radiometricNormalization(self, referenceData, referenceGaps, imageData, imageGaps):
		validDataMask = np.logical_and(
												np.logical_and( (referenceGaps == 0), (referenceGaps != self.nodataValue) ),
												np.logical_and( (imageGaps == 0), (imageGaps != self.nodataValue) ),
										)

		validImageData = imageData[validDataMask]
		validReferenceData = referenceData[validDataMask]

		imageMean = np.mean(validImageData, axis=0)
		ImageStdDev = np.std(validImageData, axis=0)

		stdDev3Inferior = imageMean - 3 * ImageStdDev
		stdDev3Superior = imageMean + 3 * ImageStdDev

		stdDev3Mask = np.logical_and( (validImageData >= stdDev3Inferior), (validImageData <= stdDev3Superior) )

		try:
			slope, intercept, rValue, _, _ = stats.linregress(validImageData[stdDev3Mask], validReferenceData[stdDev3Mask])
			r2Value = rValue * rValue

			return intercept, slope, r2Value
		except:
			return None, None, 0

	def process(self, message):
		utils.log(self.name, 'Executing module Composite')

		images = message.get('images')
		compositeParams = message.get('composite_params')
		
		outputDir = os.path.join(self.module_path, compositeParams['spectral_index'])
		utils.createDir(outputDir)

		compositeBasepath = self.getCompositeBasepath(outputDir,compositeParams)

		referenceImage, fillImages = self.separateImage(images)
		if referenceImage is not None:
			self.fillTheGaps(referenceImage, fillImages, compositeBasepath)

		self.publish(message);
import utils
import os
import loader
from ._module import Module

class CompleteNormalization(Module):

	def __init__(self, config):
		Module.__init__(self, config)

		self.db = loader.getDb()

	def process(self, message):
		utils.log(self.name, 'Executing module Complete')

		sensor = message.get('sensor')
		images = message.get('images')
		footprint = message.get('footprint')

		cloudMask = cloudCover = None
		if message.hasKey('cloud_mask'):
			cloudMask  = message.get('cloud_mask')
			cloudCover = footprint['cloudCover']
		
		outputDir = os.path.join(self.module_path,sensor['id'])
		utils.createDir(outputDir)

		for image in images:
			indexDict = {}

			if self.debug_flag == 1:
				utils.log(self.id(), 'DB Inserting  ', image['filepath'])

			indexDict["sensor_id"] = image['sensor_id']
			indexDict["name"] = image['name']
			indexDict["utm_srid"] = int(image['fileinfo']['srid'].split(':')[1])
			indexDict["original_spatial_resolution"] = image['original_spatial_resolution']
			
			indexDict["pixel_size"] = abs(image['fileinfo']['pixelWidth'])
			indexDict["min_x"] = image['fileinfo']['extent'][0]
			indexDict["min_y"] = image['fileinfo']['extent'][1]
			indexDict["max_x"] = image['fileinfo']['extent'][2]
			indexDict["max_y"] = image['fileinfo']['extent'][3]
			indexDict["origin_x"] = image['fileinfo']['xOrigin']
			indexDict["origin_y"] = image['fileinfo']['yOrigin']
			indexDict["size_x"] = image['fileinfo']['xSize']
			indexDict["size_y"] = image['fileinfo']['ySize']

			indexDict["acquisition_year"] = int(utils.getYear(image['aquisition_date']))
			indexDict["acquisition_doy"] = int(utils.getDOY(image['aquisition_date']))
			indexDict["acquisition_date"] = utils.getDate(image['aquisition_date'])
			
			indexDict["cover_area_km2"] = footprint['coverAreaKm2']
			indexDict["cloud_cover"] = cloudCover
			indexDict["img_filepath"] = image['filepath']
			indexDict["cloud_filepath"] = cloudMask
			indexDict["footprint"] = footprint['footprintWkt']
			
			self.db.insertIndexes(indexDict)

		self.publish(message);
import utils
import os
from _module import Module

class Ndvi(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module Ndvi')
		
		images = message.get('images');

		nirImage = None
		redImage = None

		for image in images:
			
			outputDir = os.path.join(self.module_path,image['sensor_id'])
			outputFile = os.path.join(outputDir, utils.basename(image['filename'], 'tif'));
			inputFile = os.path.join(outputDir, image['filepath'])

			utils.createDir(outputDir);

			if 'NIR' in image['band_name'].upper():
				nirImage = image
			elif 'RED' in image['band_name'].upper():
				redImage = image

		print(nirImage['filename'])
		print(redImage['filename'])

		self.publish(message);
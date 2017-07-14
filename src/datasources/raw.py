import os
import glob
from _datasource import Datasource
from communication import Message

class Raw(Datasource):

	def __init__(self, db, conf):
		Datasource.__init__(self, db, conf)

	def generateMessages(self):
		wrs = self.db.getWrs(self.rowPath)
		sensors = self.db.getAllSensors()
		for sensor in sensors:
			self._getImagesBySensor(sensor['id']);
		#message.set('start', date['start']);
		#message.set('end', date['end']);
		#message.set('tmpFiles', [])
		#message.set('startDoy', self.__getDayOfYear(date['start']).zfill(3) );
		#message.set('startYear', self.__getYear(date['start']) );

		return []

	def _getImagesBySensor(self, sensorId):
		files = glob.glob( os.path.join(self.path_images,sensorId,'*.tif') ) + \
						glob.glob( os.path.join(self.path_images,sensorId,'*.TIF') )

		files.sort();

		for f in files:
			print(os.path.basename(f))

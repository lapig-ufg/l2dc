import json
from _datasource import Datasource

class Raw(Datasource):

	def __init__(self, config):
		Datasource.__init__(self, config)

	def generateMessages(self):
		message = Message()
		#message.set('start', date['start']);
		#message.set('end', date['end']);
		#message.set('tmpFiles', [])
		#message.set('startDoy', self.__getDayOfYear(date['start']).zfill(3) );
		#message.set('startYear', self.__getYear(date['start']) );

		return message
import utils
from communication import Message
from ._datasource import Datasource

class MonthlyComposite(Datasource):

		def __init__(self, db, config):
			Datasource.__init__(self, db, config)

		def generateMessages(self):
			
			messages = []

			for interval in self.__getMonthlyIntervals():
				
				images = self.__getImagesGroupBySensor(interval)
				compositeParams = {
					'start_date': utils.dateString(interval['startDate']),
					'end_date': utils.dateString(interval['endDate']),
					'spectral_index': self.spectralIndex,
					'wrs': self.db.getWrs(self.rowPath)
				}

				message = Message.newEmptyMessage()
				message.set('images', images)
				message.set('composite_params', compositeParams)

				messages.append(message)
			
			return messages;

		def __getMonthlyIntervals(self):

			intervalStartDate = self.start.replace(day=1)
			intervalEndDate = utils.newDateEndOfMonth(intervalStartDate)
			
			intervals = []

			while(intervalEndDate <= self.end):
				intervals.append({ 'startDate': intervalStartDate, 'endDate': intervalEndDate })
				intervalStartDate = utils.newDateNextMonth(intervalStartDate)
				intervalEndDate = utils.newDateEndOfMonth(intervalStartDate)

			return intervals


		def __getImagesGroupBySensor(self, interval):
			imagesList = self.db.getSpectralIndexes(self.spectralIndex, interval['startDate'], interval['endDate'], self.rowPath)

			result = {}

			for image in imagesList:
				sensorId = image['sensor_id']
				
				if sensorId not in result:
					result[sensorId] = []

				image['center_interval_distance'] = self.__distanceFromCenterOfInterval(image, interval)

				result[sensorId].append(image)

			return result

		def __distanceFromCenterOfInterval(self, image, interval):
			
			startDOY = utils.getDOY(interval['startDate'])
			endDOY = utils.getDOY(interval['endDate'])
			centerDOY = int((endDOY - startDOY) / 2)

			return (startDOY+centerDOY) - image['acquisition_doy']

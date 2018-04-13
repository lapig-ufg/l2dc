import json
from ._datasource import Datasource

class Ndvi(Datasource):

		def __init__(self, db, config):
			Datasource.__init__(self, db, config)

		def generateMessages(self):
			return [];

		def __getDates(self):
		
			startDate = self.__convertDate(self.start)
			endDate = self.__convertDate(self.end)

			productStartDate = self.__convertDate(self.productStart)
			productEndDate = self.__convertDate(self.productEnd)

			if startDate < productStartDate:
				startDate = productStartDate
			if endDate > productEndDate:
				endDate = productEndDate

			dateList = []

			start = startDate
			end = start
			
			temporalResolution = self.temporalResolution
			if self.temporalResolution > 1:
				temporalResolution -= 1

			while end < endDate:

				end = start + datetime.timedelta(days=temporalResolution)

				if start.year != end.year:
					end = start + datetime.timedelta(days=(31 - start.day))

				if end > endDate:
						end = endDate

				dateList.append(
						{
								"start" : start.strftime("%Y-%m-%d"),
								"end" : end.strftime("%Y-%m-%d")
						}
				)

				start = end
				start = start + datetime.timedelta(days=1)

			return dateList
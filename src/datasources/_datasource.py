import time
import loader
import subprocess
import json
import datetime
import inspect
from communication import Message

class Datasource:
	def __init__(self, db, config):
		self.db = db;
		for key in config:
			setattr(self, key, config[key])

	def __getYear(self, strDate):
		return str(self.__convertDate(strDate).timetuple().tm_year)

	def __getDayOfYear(self, strDate):
		return str(self.__convertDate(strDate).timetuple().tm_yday)

	def __getTiles(self):
		sql = "SELECT A.TILES FROM {grid} A, {region} B WHERE ST_Intersects(A.geometry, B.geometry)".format( grid=self.gridName, region=self.region.capitalize() )
		command = "ogr2ogr -f GeoJSON -sql \"{sql}\" -dialect SQLITE /vsistdout/ {shpDir}".format( sql=sql, shpDir=self.path_shp)

		p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		(output, err) = p.communicate()

		geoJson = json.loads(unicode(output, "utf-8"))
		tiles = []

		for feature in geoJson['features']:
			tiles.append(feature['properties']['TILES'])

		return tiles

	def __convertDate(self, strDate):
		try:
				if strDate is None:
					return datetime.datetime.now()
				else:
					return datetime.datetime.strptime(strDate, "%Y-%m-%d")
		except:
				exit("[DOWNLOAD MODULE ] |-> Error: '%s' have a " % strDate \
								+ "wrong date format, use YYYY-MM-DD")
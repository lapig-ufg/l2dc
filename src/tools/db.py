import sqlite3

class Db():

	def __init__(self, conf):
		self.conn = sqlite3.connect(conf['path_metadata_db']);
		self.conn.row_factory = self.__dict_factory;
		
		self.conn.enable_load_extension(True);
		self.conn.execute("SELECT load_extension('mod_spatialite');");

		self.cursor = self.conn.cursor();

	def getWrs(self, wrsId):
		self.cursor.execute("SELECT id, utm_srid, mean_solar_azimuth, mean_solar_zenith, asWkt(Geometry) as Geometry FROM wrs WHERE id = ?",(wrsId,));
		result = self.cursor.fetchall();
		return result[0];

	def insertIndexes(self, indexDict):

		sql = "INSERT INTO indexes(" + \
					"sensor_id,	name,	utm_srid,	original_spatial_resolution, " + \
					"pixel_size,	min_x,	min_y,	max_x,	max_y,	origin_x,	origin_y,	size_x,	size_y, "	 + \
					"acquisition_year,	acquisition_doy,	acquisition_date,	cover_area_km2,	cloud_cover,	img_filepath,	cloud_filepath, " + \
					"footprint )" + \
					" VALUES " + \
					"( ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, GeomFromText(?,4326) )"

		params = (
			indexDict["sensor_id"],
			indexDict["name"],
			indexDict["utm_srid"],
			indexDict["original_spatial_resolution"],
			indexDict["pixel_size"],
			indexDict["min_x"],
			indexDict["min_y"],
			indexDict["max_x"],
			indexDict["max_y"],
			indexDict["origin_x"],
			indexDict["origin_y"],
			indexDict["size_x"],
			indexDict["size_y"],
			indexDict["acquisition_year"],
			indexDict["acquisition_doy"],
			indexDict["acquisition_date"],
			indexDict["cover_area_km2"],
			indexDict["cloud_cover"],
			indexDict["img_filepath"],
			indexDict["cloud_filepath"],
			indexDict["footprint"]
		)

		self.cursor.execute(sql, params)
		self.conn.commit()

	def intersectsWithWrs(self, wrsId, extent, sridNumber):
		wktPolygon = "POLYGON((" + \
									str(extent[0]) + " " + str(extent[1]) + "," + \
									str(extent[2]) + " " + str(extent[1]) + "," + \
									str(extent[2]) + " " + str(extent[3]) + "," + \
									str(extent[0]) + " " + str(extent[3]) + "," + \
									str(extent[0]) + " " + str(extent[1]) + "))";
		
		sql = "SELECT ST_INTERSECTS(Geometry,st_Transform(GeomFromText('"+wktPolygon+"',?),4326)) AS intersects FROM wrs WHERE id = ?";
		
		self.cursor.execute(sql,(int(sridNumber),wrsId,));
		result = self.cursor.fetchall();

		return result[0]['intersects'];

	def getBands(self, sensorId):
		self.cursor.execute("SELECT * FROM bands WHERE sensor_id = ?",(sensorId,));
		return self.cursor.fetchall();

	def getSpectralIndexes(self, indexName, startDate, endDate, wrsId):

		sql = "SELECT i.id, i.sensor_id, i.name, i.utm_srid, i.original_spatial_resolution," + \
						" i.pixel_size, i.min_x, i.min_y, i.max_x, i.max_y, i.origin_x, i.origin_y, i.size_x," + \
						" i.size_y, i.acquisition_year, i.acquisition_doy, i.acquisition_date, i.cover_area_km2," + \
						" i.cloud_cover, i.img_filepath, i.cloud_filepath" + \
					" FROM indexes i, wrs w" + \
					" WHERE (name = ? AND acquisition_date >= ? AND acquisition_date <= ?)" + \
						" AND (w.id = ? AND ST_INTERSECTS(w.Geometry, i.footprint))"

		params = (indexName, startDate, endDate, wrsId)
		self.cursor.execute(sql,params);

		return self.cursor.fetchall();

	def getCloudScreening(self, sensorId):
		self.cursor.execute("SELECT * FROM cloud_screening WHERE sensor_id = ?",(sensorId,));
		print(sensorId)
		result = self.cursor.fetchall();
		return result[0];

	def getAllSensors(self):
		self.cursor.execute("SELECT * FROM sensors");
		return self.cursor.fetchall();

	def __dict_factory(self, cursor, row):
		d = {}
		
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		
		return d
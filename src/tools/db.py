import sqlite3

class Db():

	def __init__(self, conf):
		conn = sqlite3.connect(conf['path_metadata_db']);
		conn.row_factory = self.__dict_factory;
		
		conn.enable_load_extension(True);
		conn.execute("SELECT load_extension('mod_spatialite');");

		self.cursor = conn.cursor();

	def getWrs(self, wrsId):
		self.cursor.execute("SELECT id, utm_srid, asWkt(Geometry) as Geometry FROM wrs WHERE id = ?",(wrsId,));
		result = self.cursor.fetchall();
		return result[0];

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

	def getSpectralBands(self, sensorId):
		self.cursor.execute("SELECT * FROM spectral_bands WHERE sensor_id = ?",(sensorId,));
		return self.cursor.fetchall();

	def getAllSensors(self):
		self.cursor.execute("SELECT * FROM sensors");
		return self.cursor.fetchall();

	def __dict_factory(self, cursor, row):
		d = {}
		
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		
		return d
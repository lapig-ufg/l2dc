import sqlite3

class Db():

	def __init__(self, conf):
		conn = sqlite3.connect(conf['path_metadata_db']);
		conn.row_factory = sqlite3.Row;
		
		conn.enable_load_extension(True);
		conn.execute("SELECT load_extension('mod_spatialite');");

		self.cursor = conn.cursor();

	def getWrs(self, wrsId):
		self.cursor.execute("SELECT utm_srid, asWkt(Geometry) as Geometry FROM wrs WHERE id = ?",(wrsId,));
		return self.cursor.fetchall();

	def getAllSensors(self):
		self.cursor.execute("SELECT * FROM sensors");
		return self.cursor.fetchall();
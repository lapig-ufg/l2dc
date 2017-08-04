import os
import glob
import utils
from tools import gdal_utils
from datetime import datetime
from _datasource import Datasource
from communication import Message

class Raw(Datasource):

	def __init__(self, db, conf):
		Datasource.__init__(self, db, conf)

	def generateMessages(self):
		
		sensors = self.db.getAllSensors()
		
		meessages = [];

		for sensor in sensors:
			images = self._getImagesBySensor(sensor['id']);
			for key in images:
				message = Message();
				message.set('images',images[key]);
				meessages.append(message);

		return meessages

	def _getImagesBySensor(self, sensorId):

		posOffset = len(self.path_images) + len(sensorId) + 2;
		extensions = ['tif','TIF','jp2','JP2']
		files = [];

		for ext in extensions:
			files = files + glob.glob( os.path.join(self.path_images,sensorId,'*.'+ext) )

		files.sort();

		spectralBandsMap = {};
		spectralBands = self.db.getSpectralBands(sensorId);

		for spectralBand in spectralBands:
			
			dateType = spectralBand['fn_pattern_date_type'];
			dtStart = spectralBand['fn_pattern_date_start_pos']  + posOffset;

			bandPatrn = spectralBand['fn_pattern_band_name'];
			bandStart = spectralBand['fn_pattern_band_start_pos'] + posOffset;
			bandEnd = bandStart + len(bandPatrn);

			overpassIdStart = spectralBand['fn_pattern_overpass_id_start'] + posOffset;
			overpassIdEnd = spectralBand['fn_pattern_overpass_id_end'] + posOffset;

			for bandFile in files:
				if bandPatrn == bandFile[bandStart:bandEnd]:
					bandDate = self.__getImageDate(bandFile, dateType, dtStart);
					overpass = bandFile[overpassIdStart:overpassIdEnd];
					
					if self.start <= bandDate <= self.end:
						
						fileInfo = gdal_utils.info(bandFile)
						sridNumber = fileInfo['srid'].split(':')[1];
						intersects = self.db.intersectsWithWrs(self.rowPath, fileInfo['extent'], sridNumber)

						if intersects:
							
							wrs = self.db.getWrs(self.rowPath)

							dateStd = bandDate.strftime('%Y-%m-%d');
							key = overpass + "_" + dateStd;
							
							spectralBandCopy = spectralBand.copy();
							spectralBandCopy['aquisition_date'] = dateStd;
							spectralBandCopy['overpass_od'] = overpass;
							spectralBandCopy['filepath'] = bandFile;
							spectralBandCopy['filename'] = utils.basename(bandFile);
							spectralBandCopy['fileinfo'] = fileInfo;
							spectralBandCopy['wrs'] = wrs.copy();

							spectralBandCopy['wrs']['utm_srid'] = 'EPSG:' + str(spectralBandCopy['wrs']['utm_srid']);

							spectralBandCopy.pop('fn_pattern_band_name',None)
							spectralBandCopy.pop('fn_pattern_band_start_pos',None)
							spectralBandCopy.pop('fn_pattern_date_start_pos',None)
							spectralBandCopy.pop('fn_pattern_date_type',None)
							spectralBandCopy.pop('fn_pattern_overpass_id_end',None)
							spectralBandCopy.pop('fn_pattern_overpass_id_start',None)

							if not key in spectralBandsMap:
								spectralBandsMap[key] = [];

							spectralBandsMap[key].append(spectralBandCopy);

		return spectralBandsMap;

	def __getImageDate(self, filename, dateType, dtStart):
		if(dateType == 'DOY'):
			dateEnd = dtStart + 7;
			return datetime.strptime(filename[dtStart:dateEnd], '%Y%j')
		elif(dateType == 'DTE'):
			dateEnd = dtStart + 8;
			return datetime.strptime(filename[dtStart:dateEnd], '%Y%m%d')
		else:
			raise ValueError(dateType + ' is invalid dateType');
			
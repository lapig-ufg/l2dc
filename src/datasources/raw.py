import os
import glob
import utils
import uuid
from tools import gdal_utils
from datetime import datetime
from communication import Message
from ._datasource import Datasource

class Raw(Datasource):

	def __init__(self, db, conf):
		Datasource.__init__(self, db, conf)

	def generateMessages(self):
		
		sensors = self.db.getAllSensors()
		
		meessages = [];

		for sensor in sensors:
			images = self._getImagesBySensor(sensor);
			cloudScreening = self._getCloudScreeningBySensor(sensor);
			for key in images:
				message = Message.newEmptyMessage()
				message.set('images',images[key]);
				message.set('sensor',sensor);
				message.set('cloud_screening',cloudScreening);
				meessages.append(message);

		return meessages

	def _getCloudScreeningBySensor(self, sensor):
		sensorId = sensor['id'];

		return self.db.getCloudScreening(sensorId)

	def _getImagesBySensor(self, sensor):

		sensorId = sensor['id'];
		metadataSuffix = sensor['fn_suffix_metadata_file'];

		posOffset = len(self.path_images) + len(sensorId) + 2;
		extensions = ['tif','TIF','jp2','JP2']
		files = [];

		for ext in extensions:
			files = files + glob.glob( os.path.join(self.path_images,sensorId,'*.'+ext) )

		files.sort();

		bandsMap = {};
		bands = self.db.getBands(sensorId);

		for band in bands:
			
			dateType = band['fn_pattern_date_type'];
			dtStart = band['fn_pattern_date_start_pos']  + posOffset;

			bandPatrn = band['fn_pattern_band_name'];
			bandStart = band['fn_pattern_band_start_pos'] + posOffset;
			bandEnd = bandStart + len(bandPatrn);

			overpassIdStart = band['fn_pattern_overpass_id_start'] + posOffset;
			overpassIdEnd = band['fn_pattern_overpass_id_end'] + posOffset;

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
							
							bandCopy = band.copy();
							bandCopy['aquisition_date'] = dateStd;
							bandCopy['overpass_id'] = overpass;
							bandCopy['filename'] = utils.basename(bandFile);
							bandCopy['filename_noband_noext'] = self._getMetadataFile(bandPatrn, utils.basename(bandFile), '');
							bandCopy['filepath'] = bandFile;
							bandCopy['filepath_metadata'] = self._getMetadataFile(bandPatrn, bandFile, metadataSuffix);
							bandCopy['fileinfo'] = fileInfo;
							bandCopy['wrs'] = wrs.copy();

							bandCopy['wrs']['utm_srid'] = 'EPSG:' + str(bandCopy['wrs']['utm_srid']);

							bandCopy.pop('fn_pattern_band_name',None)
							bandCopy.pop('fn_pattern_band_start_pos',None)
							bandCopy.pop('fn_pattern_date_start_pos',None)
							bandCopy.pop('fn_pattern_date_type',None)
							bandCopy.pop('fn_pattern_overpass_id_end',None)
							bandCopy.pop('fn_pattern_overpass_id_start',None)

							if not key in bandsMap:
								bandsMap[key] = [];

							bandsMap[key].append(bandCopy);

		return bandsMap;

	def _getMetadataFile(self, bandPatrn, bandFile, metadataSuffix):
		if metadataSuffix is not None:
			bandPatrnAux = bandPatrn.replace('.','')
			return utils.newFileReplacePattern(bandFile, bandPatrnAux, metadataSuffix);
		else:
			return '';

	def __getImageDate(self, filename, dateType, dtStart):
		if(dateType == 'DOY'):
			dateEnd = dtStart + 7;
			return datetime.strptime(filename[dtStart:dateEnd], '%Y%j')
		elif(dateType == 'DTE'):
			dateEnd = dtStart + 8;
			return datetime.strptime(filename[dtStart:dateEnd], '%Y%m%d')
		else:
			raise ValueError(dateType + ' is invalid dateType');
			
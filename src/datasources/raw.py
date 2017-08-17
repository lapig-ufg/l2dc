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
			images = self._getImagesBySensor(sensor);
			for key in images:
				message = Message();
				message.set('images',images[key]);
				message.set('sensor',sensor);
				meessages.append(message);

		return meessages

	def _getImagesBySensor(self, sensor):

		sensorId = sensor['id'];
		metadataSuffix = sensor['fn_suffix_metadata_file'];

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
							spectralBandCopy['overpass_id'] = overpass;
							spectralBandCopy['filename'] = utils.basename(bandFile);
							spectralBandCopy['filename_noband_noext'] = self._getMetadataFile(bandPatrn, utils.basename(bandFile), '');
							spectralBandCopy['filepath'] = bandFile;
							spectralBandCopy['filepath_metadata'] = self._getMetadataFile(bandPatrn, bandFile, metadataSuffix);
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
			
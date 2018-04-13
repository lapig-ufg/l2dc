import os
import gdal
import numpy
import ogr
import osr
import utils
import loader
from tools import gdal_utils
from ._module import Module
class Footprint(Module):

	def __init__(self, config):
		Module.__init__(self, config)

		self.geoJsonDriver = ogr.GetDriverByName("GeoJSON")

		self.outSpatialRef = osr.SpatialReference()
		self.outSpatialRef.ImportFromEPSG(4326)

	def process(self, message):
		utils.log(self.name, 'Executing module Complete')

		sensor = message.get('sensor')
		images = message.get('images')
		
		outputDir = os.path.join(self.module_path, sensor['id'])
		utils.createDir(outputDir)

		coverAreaKm2, footprintWkt = self.getFootprint(images[0], outputDir)
		footprintDict = {}
		footprintDict['coverAreaKm2'] = coverAreaKm2
		footprintDict['footprintWkt'] = footprintWkt
		
		if message.hasKey('cloud_mask'):
			cloudMask  = message.get('cloud_mask')
			cloudCover = self.getCloudCover(coverAreaKm2, cloudMask)
			footprintDict['cloudCover'] = cloudCover

		message.set('footprint', footprintDict)
		self.publish(message);

	def getCloudCover(self, coverArea, cloudMask):
			
		imageDs = gdal.Open(cloudMask,gdal.GA_ReadOnly)
		Xsize = imageDs.RasterXSize 
		YSize = imageDs.RasterYSize

		totalSum = 0
		for x in range(Xsize):
			data = imageDs.GetRasterBand(1).ReadAsArray(x,0,1,YSize);
			data = numpy.where( data == 1, 1, 0)
			totalSum = totalSum + numpy.sum(data);

		cloudArea = (totalSum * 900) / 1000000

		return cloudArea / coverArea

	def getFootprint(self, baseImage, outputDir):
		filepathNobandNoExt = baseImage['filename_noband_noext']
		outputFile = os.path.join(outputDir, filepathNobandNoExt + '.geojson')

		gdal_utils.footprint(baseImage['filepath'], baseImage['nodata_value'], outputFile)
		coverAreaKm2, footprintWkt = self.getAreaAndGeometry(outputFile)
		utils.removeFile(outputFile)

		return coverAreaKm2, footprintWkt

	def getAreaAndGeometry(self, outputFile):

		dataSource = self.geoJsonDriver.Open(outputFile, 0)

		layer = dataSource.GetLayer()
		layer.SetAttributeFilter("DN = 255")

		layerSpatialRef = layer.GetSpatialRef()

		inSpatialRef = osr.SpatialReference()
		inSpatialRef.ImportFromWkt(layerSpatialRef.ExportToWkt())

		coordTransform = osr.CoordinateTransformation(inSpatialRef, self.outSpatialRef) 

		aggGeometry = None
		for feature in layer:
			geometry = feature.GetGeometryRef()
			geometry = geometry.ConvexHull()

			if aggGeometry is None:
				aggGeometry = geometry
			else:
				aggGeometry = aggGeometry.Union(geometry)
		
		aggGeometry = aggGeometry.ConvexHull()
		areaKm2 = aggGeometry.Area() / 1000000
			
		aggGeometry.Transform(coordTransform)
		geometryWktWGS84 = aggGeometry.ExportToWkt()

		return areaKm2, geometryWktWGS84
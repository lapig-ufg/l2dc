#!/usr/bin/python

import osr
import sys
import gdal
import math
import numpy
from scipy import signal

circle_conv_10px_weights = [
		[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
	,	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
	,	[0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
	,	[0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
	,	[0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0]
	,	[0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0]
	,	[0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
	,	[0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
	,	[0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
	,	[0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
	,	[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
	,	[0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
	,	[0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
	,	[0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
	,	[0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
	,	[0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0]
	,	[0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0]
	,	[0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
	,	[0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
	,	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
	,	[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
]

circle_conv_2px_weights = [
		[0.0, 0.0, 1.0, 0.0, 0.0]
	,	[0.0, 1.0, 1.0, 1.0, 0.0]
	,	[1.0, 1.0, 1.0, 1.0, 1.0]
	,	[0.0, 1.0, 1.0, 1.0, 0.0]
	,	[0.0, 0.0, 1.0, 0.0, 0.0]
]

def read_image(img_filename, band_number = 1):
	imageDs = gdal.Open(img_filename, gdal.GA_ReadOnly)
	data = imageDs.GetRasterBand(band_number).ReadAsArray(0,0,imageDs.RasterXSize,imageDs.RasterYSize)

	return imageDs, data

def write_image_output(out_filename, data, ref_image_ds):

	originX, pixelWidth, _, originY, _, pixelHeight  = ref_image_ds.GetGeoTransform()
	Xsize = ref_image_ds.RasterXSize 
	YSize = ref_image_ds.RasterYSize

	driver = gdal.GetDriverByName('GTiff')
	outRaster = driver.Create(out_filename, Xsize, YSize, 1, gdal.GDT_Int16)
	outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
	outband = outRaster.GetRasterBand(1)
	outband.WriteArray(data)
	outRasterSRS = osr.SpatialReference()
	outRasterSRS.ImportFromWkt(ref_image_ds.GetProjectionRef())
	outRaster.SetProjection(outRasterSRS.ExportToWkt())
	outband.FlushCache()

def roll_without_reintroduced(data, x_shift, y_shift):
	dataRolled = numpy.roll(data, shift=y_shift, axis=0)
	dataRolled = numpy.roll(dataRolled, shift=x_shift, axis=1)
	ySize, xSize = dataRolled.shape

	if y_shift != 0:
		if y_shift < 0:
			y_shift = -1*y_shift
		startY = ySize - y_shift
		dataRolled[startY:ySize,:] = 0
		
	if x_shift != 0:
		if x_shift < 0:
			x_shift = -1*x_shift
		startX = xSize - x_shift
		dataRolled[:,startX:xSize] = 0

	return dataRolled

def cloud_mask(blue_data, blue_radiance_th):
	first_cloud_mask = numpy.where(blue_data > blue_radiance_th, 1, 0)
	cloud_mask_buffer = signal.convolve2d(first_cloud_mask, circle_conv_10px_weights, mode= 'same')
	second_cloud_mask = numpy.where(numpy.logical_and(blue_data > (blue_radiance_th - blue_radiance_th*0.10), cloud_mask_buffer == 1), 1, 0)

	return numpy.logical_or(first_cloud_mask, second_cloud_mask)

def shadow_mask(nir_data, nir_radiance_th, cloud_mask, sun_azimuth_angle, sun_zenith_angle, pixel_size):
	potential_shadow = numpy.where(nir_data < nir_radiance_th, 1, 0)

	azi_rad = ((sun_azimuth_angle * math.pi) / 180) + (0.5 * math.pi)
	zen_rad = (0.5 * math.pi) - ((sun_zenith_angle * math.pi) / 180)

	projected_shadow = None
	cloudHeight = [100,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,6000,7000,8000,9000,10000]

	for altitude in cloudHeight:

		shadow_distance = math.tan(zen_rad) * altitude
		x = int((math.cos(azi_rad) * shadow_distance) / pixel_size)
		y = int((math.sin(azi_rad) * shadow_distance) / pixel_size)

		cloud_rolled = roll_without_reintroduced(cloud_mask, x, y)
		
		if projected_shadow is None:
			projected_shadow = cloud_rolled
		else:
			projected_shadow = numpy.logical_or(projected_shadow, cloud_rolled)

	shadow_mask = numpy.logical_and(potential_shadow, projected_shadow)
	#signal.convolve2d(shadow_mask, circle_conv_2px_weights, mode= 'same')
	return shadow_mask

def rad_slice(blue_filepath, nir_filepath, output_filepath, blue_radiance_th, nir_radiance_th, mean_zenith, mean_azimuth, nodata_value):
	
	_, blue_data = read_image(blue_filepath)
	nir_ds, nir_data = read_image(nir_filepath)
	_, pixel_size, _, _, _, _  = nir_ds.GetGeoTransform()

	cloud_data = cloud_mask(blue_data, blue_radiance_th)
	shadow_data = shadow_mask(nir_data, nir_radiance_th, cloud_data, mean_azimuth, mean_zenith, pixel_size)
	cloud_shadow_data = numpy.logical_or(shadow_data, cloud_data)

	cloud_shadow_data = numpy.where(blue_data == nodata_value, nodata_value, cloud_shadow_data)

	write_image_output(output_filepath, cloud_shadow_data, nir_ds)
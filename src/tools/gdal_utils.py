import re
import os
import gdal
import osr
import subprocess
import utils

gdal.UseExceptions();

DEFAULT_FORMAT = 'GTiff' #HFA

TIF_CREATION_OPTIONS = ["COMPRESS=LZW", "INTERLEAVE=BAND", "BIGTIFF=IF_NEEDED"]
HFA_CREATION_OPTIONS = ["COMPRESSED=YES"]

ABC_LETTERS = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

FNULL = open(os.devnull, 'w')

def vrtStack(inputFiles, outputFile):
	command = ["gdalbuildvrt", '-separate', '-overwrite', outputFile];

	for inputFile in inputFiles:
		command.append(inputFile);

	subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def stack(inputFiles, outputFile, output_format = DEFAULT_FORMAT):
	command = ["gdal_merge.py", '-of', output_format, '-separate', '-o', outputFile];

	__setCreationOption(command, '-co')

	for inputFile in inputFiles:
		command.append(inputFile);

	#print(" ".join(command))
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def destack(inputFile, outputFiles, output_format = DEFAULT_FORMAT):

	for i in range(0,len(outputFiles)):
		outputFile = outputFiles[i]
		
		command = ["gdal_translate", '-of', output_format, '-b', str(i+1) ];
		__setCreationOption(command, '-co')
		command += [inputFile, outputFile];
		
		#print(" ".join(command))
		subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def calc(inputFiles, outputFile, expression, dataType, noData, output_format = DEFAULT_FORMAT):
	
	command = ["gdal_calc.py", "--format="+output_format]
	
	for i in range(0,len(inputFiles)):
		inputFile = inputFiles[i]
		
		letter = "-" + ABC_LETTERS[i]
		expression = expression.replace("{"+str(i)+"}",ABC_LETTERS[i])

		command += [letter, inputFile]

	command += ['--NoDataValue=' + str(noData)]
	command += ["--type=" + dataType]
	command += ["--outfile=" + outputFile]
	command += ["--calc=" + '(' + expression + ')']
	__setCreationOption(command, '--co=', True)

	print(" ".join(command))

	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def mosaic(inputFiles, outputFile, nodata = None, pixelSize = None, output_format = DEFAULT_FORMAT):
	command = ["gdal_merge.py", '-of', output_format ]

	if nodata is not None:
		command += ["-n", str(nodata)]
		command += ["-a_nodata", str(nodata)]

	if pixelSize is not None:
		command += ["-ps", str(pixelSize), str(pixelSize)]

	command += ["-o", outputFile]
	__setCreationOption(command, '-co')

	inputFiles.sort()
	
	command += inputFiles
	
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def wkt2epsg(wkt, epsg='/usr/share/proj/epsg', forceProj4=False):
	
	code = None
	p_in = osr.SpatialReference()
	s = p_in.ImportFromWkt(wkt)
	if s == 5:  # invalid WKT
			return None
	if p_in.IsLocal() == 1:  # this is a local definition
			return p_in.ExportToWkt()
	if p_in.IsGeographic() == 1:  # this is a geographic srs
			cstype = 'GEOGCS'
	else:  # this is a projected srs
			cstype = 'PROJCS'
	an = p_in.GetAuthorityName(cstype)
	ac = p_in.GetAuthorityCode(cstype)
	if an is not None and ac is not None:  # return the EPSG code
			return '%s:%s' % \
					(p_in.GetAuthorityName(cstype), p_in.GetAuthorityCode(cstype))
	else:  # try brute force approach by grokking proj epsg definition file
			p_out = p_in.ExportToProj4()
			if p_out:
					if forceProj4 is True:
							return p_out
					f = open(epsg)
					for line in f:
							if line.find(p_out) != -1:
									m = re.search('<(\\d+)>', line)
									if m:
											code = m.group(1)
											break
					if code:  # match
							return 'EPSG:%s' % code
					else:  # no match
							return None
			else:
					return None

def isValid(imageFile):
	try:
		imageDs = gdal.Open(imageFile)
		imageDs.RasterCount;
		return True;
	except:
		return False;

def convertDataType(imageFile, newDataType, noDataValue=0):
	outputFile = imageFile.replace('.tif','2.tif')

	command = ["gdal_translate" ]

	command += [ '-ot', newDataType ]
	command += [ '-a_nodata',  str(noDataValue) ]
	__setCreationOption(command, '-co')
	command += [imageFile, outputFile]

	print(" ".join(command))

	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

	utils.removeFile(imageFile)
	utils.moveFile(outputFile, imageFile)

def footprint(imageFile, noDataValue, outputFile):
	bboxFile = imageFile.replace('.tif','bbox.tif')

	command = [ "gdalwarp" ]
	command += [ '-srcnodata', str(noDataValue) ]
	command += [ '-dstalpha', '-of', 'GTiff' ]
	command += [ imageFile, bboxFile ]

	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)
	print(" ".join(command))

	command = ["gdal_polygonize.py", bboxFile, '-b', '2', '-f', 'GeoJSON', outputFile]
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)
	print(" ".join(command))

	utils.removeFile(bboxFile)

def fitToBounds(inputImage, fitImage, outputFile, output_format=DEFAULT_FORMAT):
	
	outputFileVrt = outputFile + '.vrt'
	fitImageInfo = info(fitImage)
	extent = fitImageInfo['extent']

	command = ["gdalbuildvrt", '-te']
	command += [str(extent[0])]
	command += [str(extent[1])]
	command += [str(extent[2])]
	command += [str(extent[3])]
	command += [outputFileVrt]
	command += [inputImage]
	
	print(" ".join(command))

	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

	command = ["gdal_translate", '-of', output_format]
	__setCreationOption(command, '-co')
	command += [outputFileVrt, outputFile]

	print(" ".join(command))

	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

	utils.removeFile(outputFileVrt)

def info(imageFile):
	imageDs = gdal.Open(imageFile)
	
	imageSrs = osr.SpatialReference()
	imageSrs.ImportFromWkt(imageDs.GetProjection())

	xOrigin, pixelWidth, zDummy, yOrigin, zDummy2, pixelHeight = imageDs.GetGeoTransform()

	minx = xOrigin
	maxy = yOrigin
	maxx = minx + pixelWidth * imageDs.RasterXSize
	miny = maxy + pixelHeight * imageDs.RasterYSize
	extent = [minx, miny, maxx, maxy]

	band = imageDs.GetRasterBand(1);
	bandtype = gdal.GetDataTypeName(band.DataType);

	result = {
		"xSize": imageDs.RasterXSize,
		"ySize": imageDs.RasterYSize,
		"xOrigin": xOrigin,
		"yOrigin": yOrigin,
		"pixelWidth": pixelWidth,
		"pixelHeight": pixelHeight,
		"srid": wkt2epsg(imageDs.GetProjection()),
		"extent": extent,
		"nBands": imageDs.RasterCount,
		"dataType": bandtype.upper(),
		"format": imageDs.GetDriver().LongName
	};

	return result;

def reproject(imageFile, outputFile, srid, srcNodata = 0, dstNodata = 0, dstDataType="Int16", output_format=DEFAULT_FORMAT):
	
	outputFileVrt = outputFile + '.vrt'
	command = ["gdalwarp", '-of', 'vrt']
	
	command += [ '-t_srs' , srid ]
	command += [ '-srcnodata', str(srcNodata) ]
	command += [ '-dstnodata', str(dstNodata) ]
	command += [ '-ot', dstDataType ]
	command += [ imageFile, outputFileVrt ]

	print(" ".join(command))
	subprocess.call(command, stderr=subprocess.STDOUT)

	command = ["gdal_translate", '-of', output_format]
	__setCreationOption(command, '-co')
	command += [outputFileVrt, outputFile]

	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

	utils.removeFile(outputFileVrt)

def convertToGeotiff(imageFile, outputFile):
	
	command = ["gdal_translate", '-of', 'GTiff']
	__setCreationOption(command, '-co')
	command += [imageFile, outputFile]

	print(" ".join(command))

	subprocess.call(command, stderr=subprocess.STDOUT)

def resample(imageFile, outputFile, pixelSize, output_format=DEFAULT_FORMAT):
	
	outputFileVrt = outputFile + '.vrt'
	command = ["gdalwarp", '-of', 'vrt', '-tr' , str(pixelSize), str(pixelSize), imageFile, outputFileVrt]
	
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

	command = ["gdal_translate", '-of', output_format]
	__setCreationOption(command, '-co')
	command += [outputFileVrt, outputFile]

	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

	utils.removeFile(outputFileVrt)

def clip(imageFile, outputFile, shapeFile, nodata = None, output_format=DEFAULT_FORMAT):
	command = ["gdalwarp", '-of', output_format, "-crop_to_cutline", "-cutline", shapeFile]

	__setCreationOption(command, '-co')

	if nodata is not None:
		command += ["-srcnodata", str(nodata)]
		command += ["-dstnodata", str(nodata)]

	command += [imageFile, outputFile]

	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def clipCmd(pathClipCmd, imageFile, outputFile, shapeFile, nodata = None):
	command = [pathClipCmd, shapeFile, imageFile, outputFile]

	if nodata is not None:
		command += [str(nodata)]

	subprocess.call(command, stdout=subprocess.PIPE)

def __setCreationOption(command, prefix, output_format=DEFAULT_FORMAT, concat = False):

	optionsArray = []
	if output_format == 'HFA':
		optionsArray = HFA_CREATION_OPTIONS
	elif output_format == 'GTiff':
		optionsArray = TIF_CREATION_OPTIONS

	for copt in optionsArray:
		if concat == True:
			command += [ str(prefix) + str(copt) ]
		else:
			command += [ prefix, copt ]
	
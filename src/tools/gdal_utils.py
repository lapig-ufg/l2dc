import re
import os
import gdal
import osr
import subprocess

gdal.UseExceptions();

TIF_CREATION_OPTIONS = ["COMPRESS=LZW", "INTERLEAVE=BAND", "BIGTIFF=IF_NEEDED"]
ABC_LETTERS = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

def vrtStack(inputFiles, outputFile):
	command = ["gdalbuildvrt", '-separate', '-overwrite', outputFile];

	for inputFile in inputFiles:
		command.append(inputFile);

	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def stack(inputFiles, outputFile):
	command = ["gdal_merge.py", '-separate', '-o', outputFile];

	__setCreationOption(command, '-co')

	for inputFile in inputFiles:
		command.append(inputFile);


	FNULL = open(os.devnull, 'w')
	print(" ".join(command))
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def destack(inputFile, outputFiles):

	for i in xrange(0,len(outputFiles)):
		outputFile = outputFiles[i]
		
		command = ["gdal_translate",'-b', str(i+1) ];
		__setCreationOption(command, '-co')
		command += [inputFile, outputFile];
		
		FNULL = open(os.devnull, 'w')
		print(" ".join(command))
		subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def calc(inputFiles, outputFile, expression, dataType, noData):
	
	command = ["gdal_calc.py"]
	
	for i in xrange(0,len(inputFiles)):
		inputFile = inputFiles[i]
		
		letter = "-" + ABC_LETTERS[i]
		expression = expression.replace("{"+str(i)+"}",ABC_LETTERS[i])

		command += [letter, inputFile]

	command += ['--NoDataValue=' + str(noData)]
	command += ["--type=" + dataType]
	command += ["--outfile=" + outputFile]
	command += ["--calc=" + '(' + expression + ')']
	__setCreationOption(command, '--co=', True)

	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def mosaic(inputFiles, outputFile, nodata = None, pixelSize = None):
	command = ["gdal_merge.py"]

	if nodata is not None:
		command += ["-n", str(nodata)]
		command += ["-a_nodata", str(nodata)]

	if pixelSize is not None:
		command += ["-ps", str(pixelSize), str(pixelSize)]

	command += ["-o", outputFile]
	__setCreationOption(command, '-co')

	print(inputFiles)

	inputFiles.sort()
	
	command += inputFiles
	
	FNULL = open(os.devnull, 'w')
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

def reproject(imageFile, outputFile, srid):
	command = ["gdalwarp", '-t_srs' , srid]

	__setCreationOption(command, '-co')

	command += [imageFile, outputFile]

	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def clip(imageFile, outputFile, shapeFile, nodata = None):
	command = ["gdalwarp", "-crop_to_cutline", "-cutline", shapeFile]

	__setCreationOption(command, '-co')

	if nodata is not None:
		command += ["-srcnodata", str(nodata)]
		command += ["-dstnodata", str(nodata)]

	command += [imageFile, outputFile]

	FNULL = open(os.devnull, 'w')
	subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

def clipCmd(pathClipCmd, imageFile, outputFile, shapeFile, nodata = None):
	command = [pathClipCmd, shapeFile, imageFile, outputFile]

	if nodata is not None:
		command += [str(nodata)]

	print(command)
	subprocess.call(command, stdout=subprocess.PIPE)

def __setCreationOption(command, prefix, concat = False):
	for copt in TIF_CREATION_OPTIONS:
		if concat == True:
			command += [ str(prefix) + str(copt) ]
		else:
			command += [ prefix, copt ]
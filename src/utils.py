from sys import exit
from os import path
from os import makedirs
from os import remove
from os import rename
from os import symlink
import shutil
import string
import datetime
import pprint
import ntpath

pp = pprint.PrettyPrinter(indent=2)

def pprint(stuff):
	pp.pprint(stuff)

def log(*arg):
	identifier = arg[0]
	
	dateStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	msgList = list(arg[1:])
	msgList = [var for var in msgList if var]
	msg = " ".join(msgList)

	print "{dateStr} [{identifier}] {msg}".format(dateStr=dateStr, identifier=identifier, msg=msg)

def createDir(dirPath):
	if not path.exists(dirPath):
		try:
			makedirs(dirPath)
		except:
			return False

	return True

def basename(filepath, ext = None):
	basename = ntpath.basename(filepath)
	
	if ext is not None:
		splited = path.splitext(basename);
		basename = splited[0] + '.' + ext

	return basename

def newBasename(filepath, suffix):
	basename = ntpath.basename(filepath)
	
	splited = path.splitext(basename);
	basename = splited[0] + suffix + splited[1]

	return basename

def createSynLink(inputFilepath, outputFilepath):
	symlink(inputFilepath, outputFilepath)

def removeDir(dirPath):
	shutil.rmtree(dirPath)

def moveFile(originFilepath, destinationFilepath):
	rename(originFilepath, destinationFilepath)

def fileExist(filepath):
	return path.exists(filepath);

def removeFileIfExist(filepath):
	if path.exists(filepath):
			remove(filepath)

def number(strNumber):
	try:
		return int(strNumber)
	except ValueError:
		return float(strNumber)

def mapDict(argv, msg):
	argd = { }

	for i in range(len(argv)):
		if argv[i] == "-d": # program specification
			try:
				argd["-d"] = argv[i + 1]
			except:
				exit(msg)
		elif argv[i] == "-p": # product
			try:
				argd["-p"] = argv[i + 1]
			except:
				exit(msg)
		elif argv[i] == "-r": # region
			try:
				argd["-r"] = argv[i + 1]
			except:
				exit(msg)
		elif argv[i] == "-s": # start date
			try:
				argd["-s"] = argv[i + 1]
			except:
				exit(msg)
		elif argv[i] == "-e": # end date
			try:
				argd["-e"] = argv[i + 1]
			except:
				exit(msg)
		elif argv[i] == "-i": # index
			try:
				argd["-i"] = argv[i + 1]
			except:
				exit(msg)
		elif argv[i] == "-t": # target path
			try:
				argd["-t"] = argv[i + 1]
			except:
				exit(msg)
		elif argv[i] == "-m": # mrt path
			try:
				argd["-m"] = argv[i + 1]
			except:
				exit(msg)

	return argd

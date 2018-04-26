#!/usr/bin/python

import os
import loader
from datetime import datetime
from sys import argv
from utils import mapDict
from multiprocessing import Process
from communication import Message

usage = """\
Usage: %s [OPTIONS]
		-d      Datasource name [Raw or MonthlyComposite]
		-r      Landsat WRS-2 row/path [i.e. 223071]
		-s      Start date of image that will be processed [i.e. 2016-01-01]
		-e      End date of images that will be processed [i.e. 2016-12-31]
		-i      Spectral index that will bem processed, mandatory for the MonthlyComposite datasource [i.e. NDVI]
""" % argv[0]

def getDatasourceConfig(argDict):
	datasource = argDict["-d"]
	rowPath = argDict["-r"]
	start = argDict["-s"]
	end = argDict["-e"]

	datasourceConfig = {
			"datasource": datasource
		,	"rowPath": rowPath
		,	"start": datetime.strptime(start, '%Y-%m-%d')
		,	"end": datetime.strptime(end, '%Y-%m-%d')
	}

	if "-i" in argDict:
		datasourceConfig['spectralIndex'] = argDict['-i']
	elif datasource == 'MonthlyComposite':
		exit(usage)

	return datasourceConfig

def main():
	argDict = mapDict(argv, usage)

	if ("-d" in argDict and "-r" in argDict \
		 and "-s" in argDict and "-e" in argDict):

		datasourceConfig = getDatasourceConfig(argDict)
		
		datasource = loader.getDatasource(datasourceConfig['datasource'], datasourceConfig)
		bus = loader.getSyncPublisher(datasource.publish_channel)

		for message in datasource.generateMessages():
		#	filename = 'msgs/client_201612/' + message.get('id') + '.json'
		#	message.save(filename)
			bus.publish(message)

		#for path in os.listdir('msgs/client_201612/'):
		#	fmsg = open('msgs/client_201612/'+path)
		#	bus.publish(Message(fmsg.read()))
					
	else:
		exit(usage)

if __name__ == "__main__":
	main()
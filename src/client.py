#!/usr/bin/python

import loader
from sys import argv
from utils import mapDict
from multiprocessing import Process
from communication import Message

usage = """\
Usage: %s [OPTIONS]
		-d      datasource name [raw]
		-r      landsat row/path [223071]
		-s      start date of image that will be download [2016-01-01]
		-e      end date of images that will be download [2016-12-31]
""" % argv[0]

def main():
	argDict = mapDict(argv, usage)

	if "-d" in argDict and "-r" in argDict \
		 and "-s" in argDict and "-e" in argDict:

		datasource = argDict["-d"].capitalize()
		rowPath = argDict["-r"]
		start = argDict["-s"]
		end = argDict["-e"]

		datasourceConfig = {
				"datasource": datasource
			,	"rowPath": rowPath
			,	"start": start
			,	"end": end
		}

		bus = loader.getBus()		
		datasource = loader.getDatasource(datasource,datasourceConfig)

		for message in datasource.generateMessages():
			print(message)
			#bus.publishMessage(datasourceName, message)
					
	else:
		exit(usage)

if __name__ == "__main__":
	main()
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
			,	"start": datetime.strptime(start, '%Y-%m-%d')
			,	"end": datetime.strptime(end, '%Y-%m-%d')
		}

		bus = loader.getSyncPublisher('Reproject')
		datasource = loader.getDatasource(datasource,datasourceConfig)

		#for message in datasource.generateMessages():
		#	filename = 'msgs/client_201612/' + message.get('id') + '.json'
		#	message.save(filename)
			#bus.publish(message)

		for path in os.listdir('msgs/client_201612/'):
			fmsg = open('msgs/client_201612/'+path)
			bus.publish(Message(fmsg.read()))
					
	else:
		exit(usage)

if __name__ == "__main__":
	main()
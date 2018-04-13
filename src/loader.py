import os
import modules
import datasources
import config
from communication import SyncPublisher, AsyncConsumerPublisher
from tools import Db
import sqlite3

instances = {}

def getAsyncConsumerPublisher(subcribe_channel, publish_channel = None, ):
	return AsyncConsumerPublisher( config.getItems('sits', 'Bus'), subcribe_channel, publish_channel )

def getSyncPublisher(publish_channel):
	return SyncPublisher( config.getItems('sits', 'Bus'), publish_channel )

def getDb():
	return Db(config.getItems('sits', 'Db'))

def getModules():

	typeName = 'modules'
	modules = []

	for moduleName in config.getSections(typeName, typeName):
		modules.append(getModule(moduleName))

	return modules

def getDatasource(datasourceName, userParams): 
	typeName = 'datasources'
	datasourceConfig = config.getItems(typeName, datasourceName)
	datasourceConfig.update(userParams)

	datasourceClass = getattr(datasources, datasourceName)
	return datasourceClass(getDb(), datasourceConfig)

def getModule(moduleName):
	typeName = 'modules'
	moduleConfig = config.getItems(typeName, moduleName)
	sitsConfig = config.getItems('sits', 'General')
	moduleConfig.update(sitsConfig)

	moduleClass = getattr(modules, moduleName)
	return moduleClass(moduleConfig)
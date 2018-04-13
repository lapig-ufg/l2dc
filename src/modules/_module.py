import time
import os
import loader
import utils
import traceback
from communication import Message

class Module:
	def __init__(self, config):
		for key in config:
			setattr(self, key, config[key])

		self.__setDefaultValues()
		
		self.worker_number = None
		self.bus = loader.getAsyncConsumerPublisher(self.subcribe_channel, self.publish_channel)
		utils.createDir(self.module_path)

	def __setDefaultValues(self):
		className = self.__class__.__name__.lower()
		
		defaultValues = {
				'subcribe_channel': className.capitalize()
			,	'name': className.capitalize()
			,	'number_of_workers': 1
			,	'sleep_time': 5
			, 'module_path': os.path.join(self.path_workdir, className)
			, 'debug_flag' : 0
		}

		for key in defaultValues:
			if not hasattr(self, key):
				setattr(self, key, defaultValues[key])

		self.number_of_workers = int(self.number_of_workers)
		self.sleep_time = float(self.sleep_time)
		self.debug_flag = int(self.debug_flag)
		
		if hasattr(self, 'publish_channel'):
			self.publish_channel = self.publish_channel.capitalize()
		else:
			self.publish_channel = None

	def preProcess(self, message):
		utils.log(self.id(), 'received message: ', message.get('id'))
		try:
			self.process(message);
			return True
		except Exception as e:
			utils.log(self.id(), 'exception in message: ', message.get('id'))
			utils.log(self.id(), traceback.format_exc())
			return True

	def run(self):
		utils.log(self.id(), 'started')
		self.bus.listen(self.preProcess)

	def id(self):
		return self.name + '-' + str(self.worker_number)

	def publish(self, message):
		if self.publish_channel is not None:
			if self.debug_flag == 2:
				utils.log(self.id(), 'publish message: ', message.serialize())
			self.bus.publish(message)
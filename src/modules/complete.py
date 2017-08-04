import utils
import os
from _module import Module

class Complete(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module Complete')
		self.publish(message);
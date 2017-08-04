import utils
import os
from _module import Module

class Toa(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module Toa')
		self.publish(message);
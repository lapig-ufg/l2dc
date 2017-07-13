import utils
import os
from _module import Module

class Reproject(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module Reproject')
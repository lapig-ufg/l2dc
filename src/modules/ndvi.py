import utils
import os
from _module import Module

class Ndvi(Module):

	def __init__(self, config):
		Module.__init__(self, config)

	def process(self, message):
		utils.log(self.name, 'Executing module Ndvi')
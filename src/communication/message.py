import json

class Message:

	def __init__(self, rawData = None):
		if rawData:
			self.dictData = json.loads(rawData)
		else:
			self.dictData = {}

	def get(self, key):
		return self.dictData[key]

	def set(self, key, value):
		self.dictData[key] = value

	def hasKey(self, key):
		return (key in self.dictData)

	def serialize(self):
		return json.dumps(self.dictData)

	def pretty(self):
		return json.dumps(self.dictData, indent=4, sort_keys=True)

	def save(self, filename):
		file = open(filename, 'w')
		file.write(self.pretty())
		file.close()
import os
import loader
import config
from sys import argv
from multiprocessing import Process
from communication import Message

def main():
	
	os.environ["PATH"] += os.pathsep + os.pathsep.join(config.getIntegrationsPath())

	for module in loader.getModules():
		for i in range(0, module.number_of_workers):
			module.worker_number = i
			p = Process(target=module.run)
			p.start()

if __name__ == "__main__":
	main()

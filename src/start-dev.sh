#!/bin/bash

while true; do
	kill $(pgrep -f 'python server.py') &> /dev/null
	python3 server.py &
	inotifywait -r -e modify,attrib,close_write,move,create,delete . &> /dev/null
done
 
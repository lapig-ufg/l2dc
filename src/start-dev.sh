#!/bin/bash

while true; do
	kill $(pgrep -f 'python server.py') &> /dev/null
	python server.py &
	inotifywait -r -e modify,attrib,close_write,move,create,delete .
done
 
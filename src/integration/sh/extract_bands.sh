#!/bin/bash

INPUT_DIR=$1
OUTPUT_DIR=$2

for input_file in $(find $INPUT_DIR -name '*.tif'); do
	nbands=$(gdalinfo $input_file | grep 'Band' | wc -l)
	for nband in $(seq 1 $nbands); do
		output_file=$OUTPUT_DIR/$(basename $input_file '.tif')"_B$nband.tif"
		echo $output_file
		gdal_translate -b $nband -co COMPRESS=LZW -co TILED=TRUE $input_file $output_file
	done
done
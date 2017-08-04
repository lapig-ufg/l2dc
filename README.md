# Landsat-Like Data Cube

## Dependencies:
 - `python >= 2.7`
 - `redis-server >= 2.8.1`
 - `python-redis >= 2.10.3`
 - `python-gdal >= 1.8`
 - `arop`

## Running:
 1. Start Redis-server
 ```
 redis-server
 ```
 2. Start Sitsd
 ```
 python server.py
 ```
 3. Send a processing 
 ```
 python -u client.py -d raw -r 223071 -s 2016-12-01 -e 2016-12-31
 ```
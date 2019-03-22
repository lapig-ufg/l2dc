# L2DC - Landsat-Like Data Cube

## Dependencies:
 - `python >= 2.7`
 - `pika >= 0.10.0`
 - `python-gdal >= 1.8`
 - `arop`

## Running:
 1. Start Rabbitmqctl
 ```
 systemctl start rabbitmq-server
 ```
 2. Start Server
 ```
 python server.py
 ```
 3. Send the messages of images processing to Raw datasource
 ```
 python -u client.py -d Raw -r 223071 -s 2016-12-01 -e 2016-12-31
 ```
 4. Send the messages of images processing to MonthlyComposite datasource
 ```
 python3 -u client.py -d MonthlyComposite -r 223071 -s 2016-12-01 -e 2016-12-31 -i NDVI
 
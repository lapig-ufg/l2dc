# L2DC - Landsat-Like Data Cube

The increasing number of sensors orbiting the earth is systematically producing larger volumes of data, which can be combined to produce more consistent satellite time series. In this study we present the Brazil Landsat-LikeData Cube, an initiative with the goal of compiling monthly observations, since 2000, compatible with the Landsat 8-OLI grid-cell (i.e. 30m), in order to produce consistent time series of biophysical images for the entire Brazilian territory. Our implementation, in progress and open-source based, combines data from 13 satellites (and different sensors), using automatic approaches to reproject, resample and co-register the images. Considering as pilot area the Landsat scene 223/71, ~2.300 images were downloaded for the entire study period and an automatic Cbers image registration evaluation was conducted. Likewise, approaches regarding cloud/shadow screening and NDVI compositing have been defined. Our results indicates that the ongoing initiative is consistent, feasible, and has the potential to contribute with studies and products related to land cover and land use mapping, carbon estimations, and monitoring of degradation processes in natural and anthropic ecosystem.

[See the conference paper for more info](http://www.cartografia.org.br/cbc/2017/trabalhos/4/333.html)

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
 python3 server.py
 ```
 3. Send the messages of images processing to Raw datasource
 ```
 python3 -u client.py -d Raw -r 223071 -s 2016-12-01 -e 2016-12-31
 ```
 4. Send the messages of images processing to MonthlyComposite datasource
 ```
 python3 -u client.py -d MonthlyComposite -r 223071 -s 2016-12-01 -e 2016-12-31 -i NDVI

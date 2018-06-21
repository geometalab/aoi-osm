## Areas-of-Interest for OpenStreetMap

![AOI of Zürich](image.png)

This repository contains the source code of my thesis, which aims to evaluate
the use of big data technologies for spatial Geodata. As use case,
Areas-of-Interest (AOI) based on OpenStreetMap data are generated.

> AOI have been introduced in GMaps around mid 2016. They highlight places with
> the highest concentration of restaurants, shops and bars in an light orange
> style.

The repository contains the following parts with individual READMEs:

* [notebooks](https://github.com/philippks/ma-osm-aoi/tree/master/notebooks): used for fast prototyping
* [webapp](https://github.com/philippks/ma-osm-aoi/tree/master/webapp): PostgreSQL implementation
* [geospark](https://github.com/philippks/ma-osm-aoi/tree/master/geospark): Apache Spark implementation

A demo web application to generate AOIs (using PostgreSQL) can be found [here](http://osm-aoi.kdev.ch).

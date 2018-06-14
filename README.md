Areas-of-Interest for OpenStreetMap

This repository contains the source code of my thesis, which aims to evaluate
the use of big data technologies for spatial Geodata. As use case,
Areas-of-Interest (AOI) based on OpenStreetMap data are generated.

> AOI have been introduced in GMaps around mid 2016. They highlight places with
> the highest concentration of restaurants, shops and bars in an light orange
> style.

A web application to generate AOIs can be found here:

## Getting Started

To run the web application locally, the following steps are necessary:

Build the docker image:
```bash
docker-compose build webapp
```

Init the database:
```
docker-compose run --rm webapp bash import_osm.sh
```
This will import the file data/switzerland.osm.pbf to the database. To change
the file, edit the import script `webapp/import_osm.sh`.

Prepare the POIs:
```
docker-compose run --rm webapp bash setup_pois.sh
```

Start the webapp container:
```bash
docker-compose up -d webapp
```

Now one can access the web interface at http://localhost:5000.


## Export AOIs

When the container is prepared for the webapp, one can export the AOIs to a
GeoJSON. Therefore use the script `create_aois.py`.

```bash
docker-compose run --rm webapp python create_aois.py --help
```

For example:
```bash
docker-compose run --rm webapp python create_aois.py --output_geojson tmp/aois.geojson
```

Or use the `--with_network_centrality` tag (this is much slower!)
```bash
docker-compose run --rm webapp python create_aois.py --output_geojson tmp/aois.geojson
```

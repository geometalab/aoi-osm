## PostgreSQL Implementation

This is the PostgreSQL implementation to generate AOIs from OpenStreetMap data.

## Web Application
To run the web application locally, the following steps are necessary:

Build the docker image:
```bash
docker-compose build webapp
```

Init the database:
```
docker-compose run --rm webapp bash import_osm.sh
```
This will import the file `data/switzerland.osm.pbf` to the database. To change
the file, edit the import script `webapp/import_osm.sh`.

Since not all OSM elements are necessary for generating AOIs, one can filter
the `osm.pbf` file before importing it. For that, osmfilter can be used. An
example is provided in the file `pbf_filter_example.sh`.

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
GeoJSON. To do that, use the script `create_aois.py`.

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

## Configure PostgreSQL

To alter the PostgreSQL configuration, the file `postgres/alter_config.sh` can be edited. The file is only executed with newly created docker container, with an empty `posgres/storage` directory.

Alternatively connect to the database yourself and execute the commands manually.

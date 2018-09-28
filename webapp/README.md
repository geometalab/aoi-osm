## PostgreSQL Implementation

This is the PostgreSQL implementation to generate AOIs from OpenStreetMap data.

## Web Application
To run the web application locally, the following steps are necessary:

Build the docker image:
```bash
docker-compose build webapp
```
Filtering the `osm.pbf` (optional):

Since not all OSM elements are necessary for generating AOIs, one can filter
the `osm.pbf` file before importing it. For that, osmfilter can be used. An
example is provided in the file `pbf_filter_example.sh`.

Init the database:
```
docker-compose run --rm webapp bash import_osm.sh
```
This will import the file `data/planet-latest.osm.pbf` to the database. To change
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

When the container is prepared for the webapp, the AOIs can be exported using the script `create_aois.py`

```bash
docker-compose run --rm webapp python create_aois.py tmp/aois.geojson
```
The AOIs extract is created and will be found in the `./tmp` directory with file name of `aois.geojson`

`--clip-boundary-path` argument clips the exported AOIs to those that intersects the boundary specified by 
Rapperswil-Jona_AL8.GeoJSON (GeoJSON file can be downloaded at https://wambachers-osm.website/boundaries/
and the file must contain only one geometry).

```bash
docker-compose run --rm webapp python create_aois.py tmp/clipped_aois.geojson --clip-boundary-path ../../data/clip/Rapperswil-Jona_AL8.GeoJson
```

The `--with-network-centrality` argument will provide a better AOIs by taking into account the network centrality using
 the closeness centrality algorithm. The resulting AOIs extract will thus include the important roads.

## Configure PostgreSQL

To alter the PostgreSQL configuration, the file `postgres/alter_config.sh` can be edited. The file is only executed with
 newly created docker container, with an empty `posgres/storage` directory.

Alternatively connect to the database yourself and execute the commands manually.


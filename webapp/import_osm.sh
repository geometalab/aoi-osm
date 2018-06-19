dropdb --if-exists gis
createdb gis
psql -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'

osm2pgsql --create --slim --number-processes 2 --cache 4096 --database gis /data/switzerland-latest-pois.osm.pbf

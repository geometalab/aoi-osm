dropdb --if-exists gis
createdb gis
psql -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
osm2pgsql --create --slim --number-processes 4 --cache 4096 --database gis /data/planet-latest-pois.osm.pbf
 

dropdb --if-exists gis
# dropdb -U postgres --if-exists gis
createdb gis
# createdb -U postgres gis
psql -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
# psql -U postgres -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
osm2pgsql --create --slim --number-processes 4 --cache 4096 --database gis /data/planet-latest-pois.osm.pbf
# osm2pgsql -U postgres --create --slim --number-processes 8 --cache 16384 --database gis /data/pbf/planet-latest-pois.osm.pbf

createdb gis
psql -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'

osm2pgsql --create --slim -C 4608 --database gis /data/switzerland-latest.osm.pbf

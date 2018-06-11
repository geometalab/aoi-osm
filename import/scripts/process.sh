psql -d gis -f create_pois_view.sql
psql -d gis -f create_clusters.sql
psql -d gis -f create_aois.sql

ogr2ogr -f GeoJSON /data/output/aois.geojson "PG:host=postgres dbname=gis user=postgres" -sql "select st_transform(hull, 4326) from aois"

from subprocess import check_call
import argparse
import psycopg2
from app.aoi_query_generator import AoiQueryGenerator


def exec_sql(sql):
    with psycopg2.connect("") as connection:
        connection.set_session(autocommit=True)

        with connection.cursor() as cursor:
            cursor.execute(sql)


parser = argparse.ArgumentParser()
parser.add_argument('--output_geojson', required=True)
parser.add_argument('--hull_algorithm', choices=['concave', 'convex'], default='convex')
parser.add_argument('--with_network_centrality', action='store_true', default=False)
args = parser.parse_args()

aois_query_generator = AoiQueryGenerator(hull_algorithm=args.hull_algorithm)

if args.with_network_centrality:
    aois_query = aois_query_generator.extended_hulls_query()
    aois_query = aois_query_generator.without_water_query(aois_query)
    aois_query = aois_query_generator.sanatize_aois_query(aois_query)

    exec_sql("""
DROP TABLE IF EXISTS aois_with_network_centrality;

CREATE TABLE aois_with_network_centrality(hull geometry);

INSERT INTO aois_with_network_centrality ({})
    """.format(aois_query))

    check_call(["rm", "-f", args.output_geojson])
    check_call(["ogr2ogr",
                "-f", "GeoJSON",
                args.output_geojson,
                "PG:host=postgres dbname=gis user=postgres",
                "-sql", "select st_transform(hull, 4326) from aois_with_network_centrality"])
else:
    aois_query = aois_query_generator.hulls_query()
    aois_query = aois_query_generator.without_water_query(aois_query)
    aois_query = aois_query_generator.sanatize_aois_query(aois_query)

    exec_sql("""
DROP TABLE IF EXISTS aois_without_network_centrality;

CREATE TABLE aois_without_network_centrality(hull geometry);

INSERT INTO aois_without_network_centrality ({})
    """.format(aois_query))

    check_call(["rm", "-f", args.output_geojson])
    check_call(["ogr2ogr",
                "-f", "GeoJSON",
                args.output_geojson,
                "PG:host=postgres dbname=gis user=postgres",
                "-sql", "select st_transform(hull, 4326) from aois_without_network_centrality"])

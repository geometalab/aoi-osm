from subprocess import check_call
import argparse
import psycopg2
import time
from app.aoi_query_generator import AoiQueryGenerator
import geopandas as gpd
import os

def exec_sql(sql):
    with psycopg2.connect("") as connection:
        connection.set_session(autocommit=True)

        with connection.cursor() as cursor:
            cursor.execute(sql)


def is_valid_file(parser, arg):
    try:
        boundary_4326 = gpd.read_file(arg)
        boundary_4326 = boundary_4326.to_crs({'init': 'epsg:4326'})
        if boundary_4326['geometry'].size > 1:
            raise ValueError(f"multiple geometry not allowed: '{arg}'")
        return boundary_4326

    except (Exception) as e:
        raise argparse.ArgumentTypeError(e) from e



parser = argparse.ArgumentParser(description='Used to export the AOIs extract`')
parser.add_argument('dest', help='file path for the exported AOIs', metavar='DEST')
parser.add_argument('--clip-boundary-path', default=None,
                    help='clips the exported AOIs to those that intersects the boundary specified in this '
                         'GeoJSON file (The file must contain only one geometry).',
                    type=lambda x: is_valid_file(parser, x), metavar='PATH')
parser.add_argument('--hull-algorithm', choices=['concave', 'convex'], default='convex',
                        help='algorthim used to create the hull (cluster)')
parser.add_argument('--with-network-centrality', action='store_true', default=False)
args = parser.parse_args()

start = time.time()
aois_query_generator = AoiQueryGenerator(hull_algorithm=args.hull_algorithm, boundary=args.clip_boundary_path)

# create directory if directory dont exist
if not os.path.exists(os.path.dirname(args.dest)):
    os.makedirs(os.path.dirname(args.dest))
    
if args.with_network_centrality:
    aois_query = aois_query_generator.extended_hulls_query()
    aois_query = aois_query_generator.without_water_query(aois_query)
    aois_query = aois_query_generator.sanitize_aois_query(aois_query)

    exec_sql("""
DROP TABLE IF EXISTS aois_with_network_centrality;

CREATE TABLE aois_with_network_centrality(hull geometry);

INSERT INTO aois_with_network_centrality ({})
    """.format(aois_query))

    check_call(["rm", "-f", args.dest])
    check_call(["ogr2ogr",
                "-f", "GeoJSON",
                args.dest,
                "PG:host=postgres dbname=gis user=postgres",
                "-sql", "select st_transform(hull, 4326) from aois_with_network_centrality"])
else:
    aois_query = aois_query_generator.hulls_query()
    aois_query = aois_query_generator.without_water_query(aois_query)
    aois_query = aois_query_generator.sanitize_aois_query(aois_query)

    exec_sql("""
DROP TABLE IF EXISTS aois_without_network_centrality;

CREATE TABLE aois_without_network_centrality(hull geometry);

INSERT INTO aois_without_network_centrality ({})
    """.format(aois_query))

    check_call(["rm", "-f", args.dest])
    check_call(["ogr2ogr",
                "-f", "GeoJSON",
                args.dest,
                "PG:host=postgres dbname=gis user=postgres",
                "-sql", "select st_transform(hull, 4326) from aois_without_network_centrality"])



print("Creating aois took {}s".format(time.time() - start))

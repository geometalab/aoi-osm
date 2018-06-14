import geopandas as gpd
import psycopg2
import fiona
import time
import logging

def query_geometries(query):
    start = time.time()
    with psycopg2.connect("") as conn:
        geometries = gpd.read_postgis(query, conn, geom_col="geometry")

    geometries.crs = fiona.crs.from_epsg(3857)
    logging.debug("geometries query took {}s".format(time.time() - start))

    return geometries

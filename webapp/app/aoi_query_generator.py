from pyproj import Proj, transform
from app.html_map import generate_map_html
from ipywidgets.embed import embed_minimal_html
import gmaps
import geojson
import osmnx as ox
import networkx as nx
import operator
import time
import fiona
from tqdm import tqdm
from app.database import query_geometries
import logging
from app import settings
import json

# hides Fiona libraries logs
logging.getLogger("Fiona").setLevel(logging.INFO)
logging.getLogger("fiona").setLevel(logging.INFO)


class AoiQueryGenerator():
    def __init__(self, location=None, hull_algorithm='convex', boundary=None):
        self.location = location
        self.hull_algorithm = hull_algorithm
        self.boundary = boundary
        ox.utils.config(cache_folder='tmp/cache', use_cache=True)

    def bbox_query(self):
        location_3857 = transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), self.location[1], self.location[0])
        location_3857 = " ".join([str(coordinate) for coordinate in location_3857])
        return """
        (SELECT ST_Buffer(ST_GeomFromText('POINT({})', 3857), {}) AS bbox)
        """.format(location_3857, settings.DEFAULT_RADIUS)


    def boundary_query(self):
        return f"""
        (WITH feature_collection AS (SELECT '{self.boundary}'::json AS features)
        SELECT ST_Transform(ST_SetSRid(ST_GeomFromGeoJSON(feature_col->>'geometry'), 4326), 3857) AS geometry
        FROM (
            SELECT json_array_elements(features->'features') AS feature_col
            FROM feature_collection
        ) AS subquery)
        """


    def polygons_query(self):
        if self.location is None:
            return "SELECT * FROM pois"

        else:
            return f"""
                SELECT *
                FROM pois 
                WHERE ST_Intersects(geometry, {self.bbox_query()}) 
                """

    def preclusters_subset_query(self):
        if self.location is None:
            if self.boundary is None:
                return "SELECT * FROM preclusters"
            else:
                return f"""
                SELECT *
                FROM preclusters
                INNER JOIN {self.boundary_query()} AS boundary ON ST_Intersects(preclusters.hull, boundary.geometry)
                """
        else:
            return f"""
            SELECT * FROM preclusters WHERE ST_Intersects(hull, {self.bbox_query()})
            """

    def clusters_query(self):
        return f"""
        WITH preclusters_subset AS ({self.preclusters_subset_query()})
        SELECT preclusters_subset.id AS precluster_id,
               pois.geometry,
               ST_ClusterDBSCAN(pois.geometry, eps := 35, minpoints := preclusters_subset.dbscan_minpts) over () AS cid
        FROM pois, preclusters_subset
        WHERE ST_Within(pois.geometry, preclusters_subset.hull)
        """

    def hulls_query(self):
        if self.hull_algorithm == 'concave':
            hull = 'ST_ConcaveHull(ST_Union(geometry), 0.999)'
        else:
            hull = "ST_ConvexHull(ST_Union(geometry))"

        return f"""
        WITH clusters AS ({self.clusters_query()})
        SELECT cid, {hull} AS geometry
        FROM clusters
        WHERE cid IS NOT NULL
        GROUP BY cid
        """

    def clusters_and_hulls_query(self):
        return f"""
        WITH clusters AS ({self.clusters_query()}),
        hulls AS ({self.hulls_query()}
        SELECT cid, geometry FROM clusters
        UNION ALL
        SELECT cid, geometry FROM hulls
            """

    def network_centrality_query(self):
        return self.extended_hulls_query() + """
        UNION

        SELECT 2 as color, geometry FROM hulls

        UNION

        SELECT 3 as color, geometry FROM intersecting_lines
        """

    def extended_hulls_query(self):
        aois = query_geometries(self.hulls_query())
        aois = aois.to_crs(fiona.crs.from_epsg(4326))
        central_nodes = []

        start = time.time()
        for aoi in tqdm(aois.geometry):
            try:
                aoi_graph = ox.graph_from_polygon(aoi.buffer(0.001), network_type='all')
                closeness_centrality = nx.closeness_centrality(aoi_graph)
                sorted_nodes = sorted(closeness_centrality.items(), key=operator.itemgetter(1), reverse=True)
                central_nodes += [node[0] for node in sorted_nodes[:len(sorted_nodes) // 10]]
            except KeyboardInterrupt:
                # leave on ctrl-c
                sys.exit(0)
            except:
                logging.debug("fetching graph failed for {}".format(aoi))

        central_nodes_ids = ', '.join([f'{key}' for key in central_nodes])
        logging.debug("calculating most central nodes for aois took {}s".format(time.time() - start))

        return """
        WITH hulls AS ({hulls_query}),
        intersecting_lines AS (
            SELECT hulls.cid, ST_Intersection(way, ST_Buffer(hulls.geometry, 50)) AS geometry FROM planet_osm_line, hulls
            WHERE osm_id = ANY(
              SELECT id FROM planet_osm_ways
              WHERE nodes && ARRAY[{central_nodes_ids}]::bigint[]
            )
            AND ST_DWithin(planet_osm_line.way, hulls.geometry, 50)
        )

        SELECT 1 AS color, ST_ConcaveHull(ST_Union(geometry), 0.99) AS geometry FROM (
          SELECT cid, geometry FROM hulls
          UNION
          SELECT cid, geometry FROM intersecting_lines
        ) AS tmp
        GROUP BY cid
        """.format(hulls_query=self.hulls_query(), central_nodes_ids=central_nodes_ids)

    def without_water_query(self, hulls_query):
        return """WITH hulls AS ({hulls_query})
        SELECT ST_Difference(hulls.geometry, coalesce((
            SELECT ST_Union(way) AS geometry FROM planet_osm_polygon
            WHERE (water IS NOT NULL OR waterway IS NOT NULL)
                  AND (tunnel IS NULL OR tunnel = 'no')
            AND st_intersects(way, hulls.geometry)
        ), 'GEOMETRYCOLLECTION EMPTY'::geometry)) AS geometry
        FROM hulls""".format(hulls_query=hulls_query)

    def sanitize_aois_query(self, aois_query):
        return """
        WITH aois AS ({aois_query}),
        sanitized_aois AS(
            SELECT ST_Simplify((ST_Dump(ST_Union(geometry))).geom, 5) AS geometry FROM aois
        )
        SELECT * FROM sanitized_aois WHERE ST_IsValid(geometry) AND NOT ST_IsEmpty(geometry)
        """.format(aois_query=aois_query)

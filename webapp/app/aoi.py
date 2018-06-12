import geopandas as gpd
import psycopg2
import fiona
from pyproj import Proj, transform
from app.html_map import generate_map_html
from ipywidgets.embed import embed_minimal_html
import gmaps
import geojson
import osmnx as ox
import networkx as nx
import operator
from tqdm import tqdm


class AoiHtmlGenerator():
    def __init__(self, location=None, hull_algorithm='convex'):
        self.location = location
        self.hull_algorithm = hull_algorithm

        ox.utils.config(cache_folder='tmp/cache', use_cache=True)

    def polygons_html(self):
        polygons = self._query_database(self._polygons_query())
        return generate_map_html(self.location, polygons, style=None)

    def clusters_html(self):
        clusters = self._query_database(self._clusters_query())
        return generate_map_html(self.location, clusters)

    def clusters_and_hulls_html(self):
        clusters_and_hulls = self._query_database(self._clusters_and_hulls_query())
        return generate_map_html(self.location, clusters_and_hulls)

    def extended_hulls_html(self):
        hulls = self._query_database(self._extended_hulls_query())
        return generate_map_html(self.location, hulls, style=None)

    def network_centrality_html(self):
        network_centrality = self._query_database(self._network_centrality_query())
        return generate_map_html(self.location, network_centrality, style='network')

    def already_generated_aois_html(self):
        aois = self._query_database("SELECT hull as geometry, 0 AS cid FROM aois;")
        return generate_map_html([47.372, 8.541], aois)

    def aois_on_gmaps_html(self):
        aois = self._query_database("SELECT hull as geometry, 0 AS cid FROM aois;")
        aois = aois.to_crs({'init': 'epsg:4326'})

        figure_layout = {
            'width': '100%',
            'height': '50em',
        }

        fig = gmaps.figure(center=[47.372, 8.541], zoom_level=16, layout=figure_layout)
        geojson_layer = gmaps.geojson_layer(geojson.loads(aois.to_json()), fill_opacity=0.01)
        fig.add_layer(geojson_layer)
        fig

        embed_minimal_html('/tmp/export.html', views=[fig])
        with open('/tmp/export.html') as f:
            return f.read()

    def _polygons_query(self):
        if self.location is None:
            return "SELECT * FROM pois"

        return """
        SELECT * FROM pois WHERE st_intersects(geometry, {bbox})
        """.format(bbox=self._bbox_query())

    def _preclusters_subset_query(self):
        if self.location is None:
            return "SELECT * FROM preclusters"

        return """
        SELECT * FROM preclusters WHERE st_intersects(hull, {bbox})
        """.format(bbox=self._bbox_query())

    def _clusters_query(self):
        return """
        WITH preclusters_subset AS ({preclusters_subset_query})
        SELECT preclusters_subset.id AS precluster_id,
               geometry,
               ST_ClusterDBSCAN(geometry, eps := 35, minpoints := preclusters_subset.dbscan_minpts) over () AS cid
        FROM pois, preclusters_subset
        WHERE ST_Within(geometry, preclusters_subset.hull)
        """.format(preclusters_subset_query=self._preclusters_subset_query())

    def _hulls_query(self):
        if self.hull_algorithm == 'concave':
            hull = 'ST_ConcaveHull(ST_Union(geometry), 0.999)'
        else:
            hull = "ST_ConvexHull(ST_Union(geometry))"

        return """
WITH clusters AS ({clusters_query})
SELECT cid, {hull} AS geometry
FROM clusters
WHERE cid IS NOT NULL
GROUP BY cid
        """.format(clusters_query=self._clusters_query(), hull=hull)

    def _network_centrality_query(self):
        return self._extended_hulls_query() + """

UNION

SELECT 2 as color, geometry FROM hulls

UNION

SELECT 3 as color, geometry FROM intersecting_lines
"""

    def _extended_hulls_query(self):
        aois = self._query_database(self._hulls_query())
        aois = aois.to_crs(fiona.crs.from_epsg(4326))
        central_nodes = []

        for aoi in tqdm(aois.geometry):
            try:
                aoi_graph = ox.graph_from_polygon(aoi.buffer(0.001), network_type='all')
                closeness_centrality = nx.closeness_centrality(aoi_graph)
                sorted_nodes = sorted(closeness_centrality.items(), key=operator.itemgetter(1), reverse=True)
                central_nodes += [node[0] for node in sorted_nodes[:len(sorted_nodes) // 10]]
            except:
                print("fetching graph failed for {}".format(aoi))

        central_nodes_ids = ', '.join([f'{key}' for key in central_nodes])

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
""".format(hulls_query=self._hulls_query(), central_nodes_ids=central_nodes_ids)

    def _clusters_and_hulls_query(self):
        return """
WITH clusters AS ({clusters_query}),
hulls AS ({hulls_query})
SELECT cid, geometry FROM clusters
UNION ALL
SELECT cid, geometry FROM hulls
        """.format(clusters_query=self._clusters_query(), hulls_query=self._hulls_query())

    def _bbox_query(self):
        location_3857 = transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), self.location[1], self.location[0])
        location_3857 = " ".join([str(coordinate) for coordinate in location_3857])

        return """
    (SELECT ST_Buffer(ST_GeomFromText('POINT({})', 3857), 1000) AS bbox)
        """.format(location_3857)

    def _query_database(self, query):
        with psycopg2.connect("") as conn:
            geometries = gpd.read_postgis(query, conn, geom_col="geometry")
            geometries.crs = fiona.crs.from_epsg(3857)
            return geometries

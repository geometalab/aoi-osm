import geopandas as gpd
import psycopg2
import fiona
from pyproj import Proj, transform
from app.html_map import generate_map_html


class AoiHtmlGenerator():
    def __init__(self, location, tags, dbscan_eps=50, dbscan_minpoints=3):
        self.location = location
        self.tags = tags
        self.dbscan_eps = dbscan_eps
        self.dbscan_minpoints = dbscan_minpoints

    def polygons_html(self):
        polygons = self._query_database(self._polygons_query())
        return generate_map_html(self.location, polygons, init_style=False)

    def clusters_html(self):
        clusters = self._query_database(self._clusters_query())
        return generate_map_html(self.location, clusters)

    def clusters_and_hulls_html(self):
        clusters_and_hulls = self._query_database(self._clusters_and_hulls_query())
        return generate_map_html(self.location, clusters_and_hulls)

    def hulls_html(self):
        hulls = self._query_database(self._hulls_query())
        return generate_map_html(self.location, hulls)

    def _polygons_query(self):
        return """
(SELECT way AS geometry FROM planet_osm_polygon
    WHERE (amenity = ANY(ARRAY{amenity_tags})
            OR shop = ANY(ARRAY{shop_tags})
            OR leisure = ANY(ARRAY{leisure_tags})
            OR landuse = ANY(ARRAY{landuse_tags}))

           AND access IS DISTINCT FROM 'private'
           AND st_within(way, {bbox}))

UNION ALL

(SELECT polygon.way AS geometry FROM planet_osm_polygon AS polygon
    INNER JOIN planet_osm_point AS point
        ON st_within(point.way, polygon.way)
    WHERE (point.amenity = ANY(ARRAY{amenity_tags})
            OR point.shop = ANY(ARRAY{shop_tags})
            OR point.leisure = ANY(ARRAY{leisure_tags})
            OR point.landuse = ANY(ARRAY{landuse_tags}))

        AND point.access IS DISTINCT FROM 'private'
        AND st_within(point.way, {bbox})
        AND polygon.building IS NOT NULL)
        """.format(bbox=self._bbox_query(), **self.tags)

    def _clusters_query(self):
        return """
WITH polygons AS ({polygons_query})
SELECT polygon.geometry AS geometry,
       ST_ClusterDBSCAN(polygon.geometry, eps := {eps}, minpoints := {minpoints}) over () AS cid
FROM polygons AS polygon
        """.format(polygons_query=self._polygons_query(), eps=self.dbscan_eps, minpoints=self.dbscan_minpoints)

    def _hulls_query(self):
        return """
WITH clusters AS ({clusters_query})
SELECT cid, ST_ConvexHull(ST_Union(geometry)) AS geometry
FROM clusters
WHERE cid IS NOT NULL
GROUP BY cid
        """.format(clusters_query=self._clusters_query())

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

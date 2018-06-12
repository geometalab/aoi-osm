from app.html_map import generate_map_html
from ipywidgets.embed import embed_minimal_html
import gmaps
import geojson
import psycopg2
import geopandas as gpd
import fiona
from app.aoi_query_generator import AoiQueryGenerator


class AoiHtmlGenerator():
    def __init__(self, location=None, hull_algorithm='convex'):
        self.query_generator = AoiQueryGenerator(location, hull_algorithm)
        self.location = location

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

    def query_database(self, query):
        with psycopg2.connect("") as conn:
            geometries = gpd.read_postgis(query, conn, geom_col="geometry")
            geometries.crs = fiona.crs.from_epsg(3857)
            return geometries

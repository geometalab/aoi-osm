from app.html_map import generate_map_html
from ipywidgets.embed import embed_minimal_html
import gmaps
import geojson
import geopandas as gpd
from app.aoi_query_generator import AoiQueryGenerator
from app.database import query_geometries


class AoiHtmlGenerator():
    def __init__(self, location=None, hull_algorithm='convex'):
        self.query_generator = AoiQueryGenerator(location, hull_algorithm)
        self.location = location

    def any_aoi(self):
        clusters = self.query_geometries(self.query_generator.clusters_query())
        return clusters.size > 0

    def polygons_html(self):
        polygons = self.query_geometries(self.query_generator.polygons_query())
        return generate_map_html(self.location, polygons, style=None)

    def clusters_html(self):
        clusters = self.query_geometries(self.query_generator.clusters_query())
        return generate_map_html(self.location, clusters)

    def clusters_and_hulls_html(self):
        clusters_and_hulls = self.query_geometries(self.query_generator.clusters_and_hulls_query())
        return generate_map_html(self.location, clusters_and_hulls)

    def network_centrality_html(self):
        network_centrality = self.query_geometries(self.query_generator.network_centrality_query())
        return generate_map_html(self.location, network_centrality, style='network')

    def extended_hulls_html(self):
        hulls = self.query_geometries(self.query_generator.extended_hulls_query())
        return generate_map_html(self.location, hulls, style=None)

    def without_water_html(self):
        query = self.query_generator.without_water_query(self.query_generator.extended_hulls_query())
        hulls = self.query_geometries(query)
        return generate_map_html(self.location, hulls, style=None)

    def aois_html(self):
        aois_query = self.query_generator.extended_hulls_query()
        aois_query = self.query_generator.without_water_query(aois_query)
        aois_query = self.query_generator.sanatize_aois_query(aois_query)

        aois = self.query_geometries(aois_query)
        return generate_map_html(self.location, aois, style=None)

    def already_generated_aois_html(self):
        aois = gpd.read_file("static/aois.geojson")
        aois = aois[aois.geometry.notnull()]
        return generate_map_html([47.372, 8.541], aois, style=None)

    def aois_on_gmaps_html(self):
        aois = gpd.read_file("static/aois.geojson")
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

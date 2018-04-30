import folium
import folium.plugins
import geopandas as gpd
import psycopg2
import fiona
from pyproj import Proj, transform


PATH = '/webapp/tmp/aoi.html'


def generate_aoi_html(location, tags):
    conn = psycopg2.connect(dbname="gis", user="postgres", password="")

    location_3857 = transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), location[1], location[0])
    location_3857 = " ".join([str(coordinate) for coordinate in location_3857])
    poi_polygons_clustered = gpd.read_postgis(_query(location_3857, tags), conn, geom_col='hull')
    n_clusters = len(poi_polygons_clustered.groupby('cid').cid.nunique())
    poi_polygons_clustered.crs = fiona.crs.from_epsg(3857)

    bbox = gpd.read_postgis(_bbox_query(location_3857), conn, geom_col='bbox')
    bbox.crs = fiona.crs.from_epsg(3857)

    m = folium.Map(location=location, zoom_start=16, tiles="cartodbpositron")

    folium.plugins.Fullscreen().add_to(m)
    folium.GeoJson(poi_polygons_clustered, style_function=init_style_function(n_clusters)).add_to(m)
    folium.GeoJson(bbox)

    m.save(PATH)

    with open(PATH) as f:
        return f.read()


def _query(location, tags):
    return """
WITH polygons AS (
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
)
, clusters AS (
    SELECT polygon.geometry AS geometry, ST_ClusterDBSCAN(polygon.geometry, eps := 50, minpoints := 3) over () AS cid
    FROM polygons AS polygon
)

SELECT cid, ST_ConcaveHull(ST_Union(geometry), 0.99) AS hull
FROM clusters
WHERE cid IS NOT NULL
GROUP BY cid
    """.format(bbox=_bbox_query(location), **tags)


def _bbox_query(location):
    return """
(SELECT ST_Buffer(ST_GeomFromText('POINT({})', 3857), 1000) AS bbox)
    """.format(location)


def rgb(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 255*(1 - ratio)))
    r = int(max(0, 255*(ratio - 1)))
    g = 255 - b - r
    return r, g, b


def style_function(feature, n_colors):
    cid = feature['properties']['cid']
    return {
        'fillOpacity': 0.5,
        'weight': 0,
        'fillColor': '#red' if cid is None else "rgb{}".format(rgb(0, n_colors, cid))
    }


def init_style_function(n_colors):
    return lambda feature: style_function(feature, n_colors)

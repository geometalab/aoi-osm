import folium
import folium.plugins


PATH = '/webapp/tmp/tmp_to_generate.html'


def generate_map_html(location, dataframe, init_style=True):
    m = folium.Map(location=location, zoom_start=16, tiles="cartodbpositron")
    folium.plugins.Fullscreen().add_to(m)

    if init_style:
        dataframe_len = len(dataframe.groupby('cid').cid.nunique())
        folium.GeoJson(dataframe, style_function=init_style_function(dataframe_len)).add_to(m)
    else:
        folium.GeoJson(dataframe).add_to(m)

    m.save(PATH)

    with open(PATH) as f:
        return f.read()


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

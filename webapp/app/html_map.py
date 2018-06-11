import folium
import folium.plugins


PATH = '/webapp/tmp/tmp_to_generate.html'


def generate_map_html(location, dataframe, style='cid'):
    m = folium.Map(location=location, zoom_start=16, tiles="cartodbpositron")
    folium.plugins.Fullscreen().add_to(m)

    if style == 'cid':
        dataframe_len = len(dataframe.groupby('cid').cid.nunique())
        folium.GeoJson(dataframe, style_function=init_style_function(dataframe_len)).add_to(m)
    elif style == 'network':
        folium.GeoJson(dataframe, style_function=network_style_function).add_to(m)
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


def network_style_function(feature):
    color = feature['properties']['color']
    weight = 0

    if color == 1:
        fillColor = "rgb(255, 0, 0)"
    elif color == 2:
        fillColor = "rgb(0, 0, 255)"
    elif color == 3:
        fillColor = "rgb(255, 255, 0)"
        weight = 3
    else:
        raise

    return {
            'fillOpacity': 0.5,
            'weight': weight,
            'fillColor': fillColor
            }

import folium


PATH = '/webapp/tmp/aoi.html'


def generate_aoi_html(location, tags):
    m = folium.Map(location=location, zoom_start=16)

    m.save(PATH)

    with open(PATH) as f:
        return f.read()

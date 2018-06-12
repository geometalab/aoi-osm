from flask import render_template
from app import app
from app.forms import AoiForm
from app.aoi import AoiHtmlGenerator


@app.route('/', methods=['GET', 'POST'])
def index():
    form = AoiForm()

    if form.validate_on_submit():
        aoi_generator = AoiHtmlGenerator(location=form.location_coordinates(),
                                         hull_algorithm=form.hull_algorithm_value())

        return render_template('aoi.html', aoi_generator=aoi_generator)

    return render_template('index.html', form=form)


@app.route('/browse', methods=['GET'])
def browse():
    generator = AoiHtmlGenerator()
    return render_template('browse.html', map_html=generator.already_generated_aois_html())


@app.route('/gmaps', methods=['GET'])
def gmaps():
    generator = AoiHtmlGenerator()
    return render_template('browse.html', map_html=generator.aois_on_gmaps_html())

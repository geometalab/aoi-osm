from flask import render_template
from app import app
from app.forms import AoiForm
from app.aoi import generate_aoi_html


@app.route('/', methods=['GET', 'POST'])
def index():
    form = AoiForm()

    aoi_html = None
    if form.validate_on_submit():
        aoi_html = generate_aoi_html(location=form.location_coordinates(), tags=form.tags_dict())

        return render_template('aoi.html', aoi_html=aoi_html)

    return render_template('index.html', form=form)

from flask import render_template
from app import app
from app.forms import AoiForm
from app.aoi import AoiHtmlGenerator


@app.route('/', methods=['GET', 'POST'])
def index():
    form = AoiForm()

    if form.validate_on_submit():
        aoi_generator = AoiHtmlGenerator(location=form.location_coordinates(),
                                         tags=form.tags_dict(),
                                         dbscan_eps=form.dbscan_eps_value(),
                                         dbscan_minpoints=form.dbscan_minpoints_value())

        return render_template('aoi.html', aoi_generator=aoi_generator)

    return render_template('index.html', form=form)

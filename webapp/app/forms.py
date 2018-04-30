import json

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, SubmitField
from wtforms.fields import StringField, IntegerField
from wtforms.widgets import TextArea

from app import settings


class AoiForm(FlaskForm):
    location = SelectField('Location', choices=settings.DEFAULT_LOCATIONS)
    custom_location = TextField('Custom Location', render_kw={"placeholder": "e.g. 47.3720, 8.5417"})
    tags = StringField('Tags', widget=TextArea(), default=settings.DEFAULT_TAGS)
    dbscan_eps = IntegerField('DBSCAN eps', default=50)
    dbscan_minpoints = IntegerField('DBSCAN minpoints', default=3)

    submit = SubmitField('Generate AOI')

    def location_coordinates(self):
        location_str = self.location.data
        if len(self.custom_location.data) > 0:
            location_str = self.custom_location.data

        return [float(x) for x in location_str.split(",")]

    def tags_dict(self):
        return json.loads(self.tags.data)

    def dbscan_eps_value(self):
        return self.dbscan_eps.data

    def dbscan_minpoints_value(self):
        return self.dbscan_minpoints.data

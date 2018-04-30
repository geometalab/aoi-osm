import json

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, SubmitField
from wtforms.fields import StringField, IntegerField
from wtforms.widgets import TextArea

from app import settings


class AoiForm(FlaskForm):
    location = SelectField('Location', choices=settings.DEFAULT_LOCATIONS)
    custom_location = TextField('Custom Location')
    tags = StringField('Tags', widget=TextArea(), default=settings.DEFAULT_TAGS)
    dbscan_eps = IntegerField('DBSCAN eps', default=50)
    dbscan_minpoints = IntegerField('DBSCAN minpoints', default=3)

    submit = SubmitField('Generate AOI')

    def location_coordinates(self):
        return [float(x) for x in self.location.data.split(",")]

    def tags_dict(self):
        return json.loads(self.tags.data)

    def dbscan_eps_value(self):
        return self.dbscan_eps.data

    def dbscan_minpoints_value(self):
        return self.dbscan_minpoints.data

import json

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, SubmitField
from wtforms.fields import StringField
from wtforms.widgets import TextArea

from app import settings


class AoiForm(FlaskForm):
    location = SelectField('Location', choices=settings.DEFAULT_LOCATIONS)
    custom_location = TextField('Custom Location')
    tags = StringField('Tags', widget=TextArea(), default=settings.DEFAULT_TAGS)

    submit = SubmitField('Generate AOI')

    def location_coordinates(self):
        return [float(x) for x in self.location.data.split(",")]

    def tags_dict(self):
        return json.loads(self.tags.data)

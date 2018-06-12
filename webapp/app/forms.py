import json

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, SubmitField
from wtforms.fields import StringField, RadioField, BooleanField
from wtforms.widgets import TextArea

from app import settings


class AoiForm(FlaskForm):
    location = SelectField('Location', choices=settings.DEFAULT_LOCATIONS)
    custom_location = TextField('Custom Location', render_kw={"placeholder": "e.g. 47.3720, 8.5417"})
    tags = StringField('Tags', widget=TextArea(), default=settings.DEFAULT_TAGS, render_kw={'readonly': True})
    hull_algorithm = RadioField('Hull Algorithm', choices=[('convex', 'Convex'), ('concave', 'Concave(0.99)')], default='convex')
    explain = BooleanField("Explain steps when generating AOIs (slower)")

    submit = SubmitField('Generate AOIs')

    def location_coordinates(self):
        location_str = self.location.data
        if len(self.custom_location.data) > 0:
            location_str = self.custom_location.data

        return [float(x) for x in location_str.split(",")]

    def tags_dict(self):
        return json.loads(self.tags.data)

    def hull_algorithm_value(self):
        return self.hull_algorithm.data

    def explain_value(self):
        return self.explain.data

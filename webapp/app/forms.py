import json

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields import StringField, RadioField, BooleanField
from wtforms.validators import ValidationError, EqualTo
from wtforms.widgets import TextArea

from app import settings


class OtherFieldNotEmpty(object):
    """
    Raises ValidationError if other field isn't populated

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if not field.data and not other.data:
            message = self.message
            if message is None:
                message = field.gettext('Either %(field_name)s OR %(other_field_name)s must be set.')

            d = {
                'other_field_name': other.label.text if hasattr(other, 'label') else self.fieldname,
                'field_name': field.label.text if hasattr(field, 'label') else 'this',
            }
            raise ValidationError(message % d)


class AoiForm(FlaskForm):
    location = SelectField('Location', choices=settings.DEFAULT_LOCATIONS, validators=[OtherFieldNotEmpty('custom_location')])
    custom_location = StringField('Custom Location', render_kw={"placeholder": "e.g. 47.3720, 8.5417"})
    tags = StringField('Tags', widget=TextArea(), default=settings.DEFAULT_TAGS, render_kw={'readonly': True})
    radius = StringField('Radius', default=settings.DEFAULT_RADIUS, render_kw={'readonly': True})
    hull_algorithm = RadioField('Hull Algorithm', choices=[('convex', 'Convex'), ('concave', 'Concave(0.99)')], default='concave')
    extend_network_centrality = BooleanField("Extend with network centrality (much slower!)")
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

    def extend_network_centrality_value(self):
        return self.extend_network_centrality.data

    def explain_value(self):
        return self.explain.data

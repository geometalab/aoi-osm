from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField
from wtforms.validators import DataRequired


class AoiForm(FlaskForm):
    location = TextField('Location', validators=[DataRequired()])
    tags = TextField('Tags')

    submit = SubmitField('Generate AOI')

    def location_coordinates(self):
        return [float(x) for x in self.location.data.split(",")]

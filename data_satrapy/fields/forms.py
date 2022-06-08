from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from data_satrapy.models import Field


class AddFieldForm(FlaskForm):
    post_subject = StringField("Add a new Field Subject",
                               validators=[DataRequired()])
    submit = SubmitField("Add Subject")

    def validate_post_subject(self, post_subject):
        post_subject = str(post_subject.data).strip().title()
        field = Field.query.filter_by(subject=post_subject).first()
        if field:
            raise ValidationError("This field already exists in the database.")


class UpdateDeleteFieldForm(FlaskForm):
    new_field = StringField("New Field Name", validators=[DataRequired()])
    submit = SubmitField("Update Field")

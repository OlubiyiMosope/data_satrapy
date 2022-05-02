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
    old_field = StringField("Existing Field", validators=[DataRequired()])
    new_field = StringField("Amendment Field", validators=[DataRequired()])
    submit = SubmitField("Update Field")
    # delete_field = SubmitField("Delete Field")

    def validate_old_field(self, old_field):
        """
        Check if old_field exists in database.
        :param old_field:
        :return: ValidationError if old_field does not exist in database
        """
        field_name = old_field.data.strip().title()  # convert to string, strip and capitalize each word.
        field = Field.query.filter_by(subject=field_name).first()
        if not field:
            raise ValidationError("This field does not exist in the database. "
                                  "Please input a field that exists in the database")


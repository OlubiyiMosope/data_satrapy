import click
from flask.cli import with_appcontext
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from data_satrapy.models import Field
# from data_satrapy import create_app


# subjects = Field.query.all()
# To list all the fields in the database (in alphabetical order)
# @click.command("list_subs")
# @with_appcontext
# def list_subs():
#     subs = [str(field) for field in Field.query.all()]
#     subs.sort()
#     return subs
#
#
# subjects = list_subs()


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    post_field = StringField("Post Field", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Create Post")


class DynamicPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    post_subject = SelectField("Select a Field Subject for your post", validators=[DataRequired()], )  # choices=subjects
    # post_subject = StringField("Select a Field Subject for your post", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Create Post")

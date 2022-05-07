from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    post_subject = SelectField("Select a Field Subject for Your Post", validators=[DataRequired()], )
    thumbnail = FileField("Post Preview Image", validators=[FileAllowed(["jpg", "png"])])  # , "JPG", "PNG"
    content = PageDownField("Content", validators=[DataRequired()])
    submit = SubmitField("Post")

from flask_wtf  import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from data_satrapy.models import User, Field


class RegistrationForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=8,)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")

    # validation to ensure that emails and usernames already existing in the database cannot be used for new accounts
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username already exists. Please choose a different one.")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("This email already exists. Please choose a different one.")


class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    post_field = StringField("Post Field", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Create Post")


# subjects = Field.query.all()
# To list all the fields in the database (in alphabetical order)
subjects = [str(field) for field in Field.query.all()]
subjects.sort()


class DynamicPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    post_subject = SelectField("Select a Field Subject for your post", validators=[DataRequired()], choices=subjects)
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Create Post")


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

from flask import render_template, url_for, flash, redirect, request
from data_satrapy import app, db, bcrypt, mail
from data_satrapy.forms import (RegistrationForm, LoginForm, DynamicPostForm, AddFieldForm,
                                UpdateDeleteFieldForm, RequestResetForm, ResetPasswordForm)
from data_satrapy.models import User, Post, Field
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


CONTENT_COL = 6
CONTENT_COL_2 = 8


# To list all the fields in the database (in alphabetical order)
def list_subjects():
    fields = [field.subject for field in Field.query.all()]
    fields.sort()

    field_ids = []
    for field in fields:
        field = Field.query.filter_by(subject=field).first()
        field_ids.append(field.id)

    return list(zip(field_ids, fields))


# subjects = list_subjects()


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()). \
        paginate(page=page, per_page=5)
    return render_template("home.html", home_active="active", posts=posts,
                           grid_size=CONTENT_COL)


@app.route("/about")
def about():
    return render_template("about.html", title="About", about_active="active",
                           grid_size=CONTENT_COL)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! You are now able to log in", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form,
                           register_active="active", grid_size=CONTENT_COL)


# *** LOGIN / LOGOUT ***

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # flash("You are already logged in.", "success")
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash("You have been logged in!", "success")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login unsuccessful! Please check username and password.", "danger")
    return render_template("login.html", title="Login", form=form,
                           login_active="active", grid_size=CONTENT_COL)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# *** POSTS ***

@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = DynamicPostForm()
    # QUERY DATABASE FOR SUBJECTS IN FIELD MODEL.
    subjects = Field.query.all()

    # if form.validate_on_submit():
    #     post = Post(title=form.title.data, content=form.content.data, author=current_user, field=1)
    #     db.session.add(post)
    #     db.session.commit()
    #     flash("Your new post has been created!", "success")
    #     return redirect(url_for("home"))
    return render_template("dynamic_post.html", title="New Post", form=form,
                           subjects=subjects, new_post_active="active", grid_size=CONTENT_COL)


@app.route("/post")
def post():

    return render_template("post.html", title="Post", grid_size=CONTENT_COL)


# *** FIELDS ***

@app.route("/field/", methods=["GET", "POST"])
@login_required
def add_field():
    form = AddFieldForm()
    subjects = list_subjects()
    if form.validate_on_submit():
        subject = str(form.post_subject.data).strip().title()
        # if not Field.query.filter_by(subject=subject).first():
        field = Field(subject=subject)
        db.session.add(field)
        db.session.commit()
        flash(f"New field '{field.subject}' has been successfully added to database", "success")
        return redirect(url_for("add_field"))  # to refresh the page
    return render_template("add_field.html", title="Add Field", form=form, add_field_active="active",
                           grid_size=CONTENT_COL_2, subjects=subjects)


@app.route("/field/<string:field_name>")
def field_posts(field_name):
    page = request.args.get("page", 1, type=int)
    subject = Field.query.filter_by(subject=field_name).first_or_404()
    posts = Post.query.filter_by(field=subject)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template("field_posts.html", title=field_name, subject=subject,
                           posts=posts, grid_size=CONTENT_COL_2)


@app.route("/field/<int:subject_id>/update", methods=["GET", "POST"])
@login_required
def update_field(subject_id):
    subjects = list_subjects()
    field = Field.query.get_or_404(subject_id)
    form = UpdateDeleteFieldForm()

    # if request.method == "POST":
    if request.form.get("delete") == "delete":
        delete_field(subject_id)
        return redirect(url_for("add_field"))

    if form.validate_on_submit():
        field.subject = form.new_field.data.strip().title()
        db.session.commit()
        flash("You have successfully updated the field", "success")
        return redirect(url_for("update_field", subject_id=subject_id))
    elif request.method == "GET":
        form.old_field.data = field.subject
        form.new_field.data = field.subject

    return render_template("update_n_del_field.html", title="Update/Delete Field",
                           form=form, subjects=subjects, grid_size=CONTENT_COL_2,
                           del_field=field.subject)


# @app.route("/field/<int:subject_id>/delete", methods=["POST"])
# @login_required
def delete_field(subject_id):
    field = Field.query.get_or_404(subject_id)
    flash(f"You have deleted the field '{field.subject}'!", "success")
    db.session.delete(field)
    db.session.commit()
    return redirect(url_for("add_field"))


# *** RESET EMAIL & PASSWORD ***

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request",
                  sender="noreply@datasatrapy.com",
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form, grid_size=CONTENT_COL_2)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password',
                           form=form, grid_size=CONTENT_COL_2)

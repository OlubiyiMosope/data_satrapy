from flask import render_template, url_for, flash, redirect, request, abort
from data_satrapy import app, db, bcrypt
from data_satrapy.forms import RegistrationForm, LoginForm, DynamicPostForm, FieldForm, UpdateDeleteFieldForm
from data_satrapy.models import User, Post, Field
from flask_login import login_user, current_user, logout_user, login_required


CONTENT_COL = 6
CONTENT_COL_2 = 8

# To list all the fields in the database (in alphabetical order)
subjects = [str(field) for field in Field.query.all()]
subjects.sort()


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
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


# app.add_url_rule("/post/new", 'new_post', new_post)


@app.route("/post")
def post():

    return render_template("post.html", grid_size=CONTENT_COL)


@app.route("/field/", methods=["GET", "POST"])
@login_required
def add_field():
    form = FieldForm()
    if form.validate_on_submit():
        subject = str(form.post_subject.data).strip().title()
        # if not Field.query.filter_by(subject=subject).first():
        field = Field(subject=subject)
        db.session.add(field)
        db.session.commit()
        flash("New field has been successfully added to database", "success")
    return render_template("add_field.html", form=form, add_field_active="active",
                           grid_size=CONTENT_COL_2, subjects=subjects)


@app.route("/field/update", methods=["GET", "POST"])
@login_required
def update_field():
    form = UpdateDeleteFieldForm()
    form.new_field.data = "New field"
    if form.validate_on_submit():  # extra_validators=None
        # use form data to get the field to update
        field = Field.query.filter_by(subject=str(form.old_field.data).title()).first()
        field.subject = str(form.new_field.data).title()  # change old field to new field
        db.session.commit()
        flash("You have successfully updated the field", "success")
    return render_template("update_n_del_field.html", form=form, subjects=subjects, grid_size=CONTENT_COL_2)


@app.route("/field/delete", methods=["POST"])
@login_required
def delete_field():
    form = UpdateDeleteFieldForm()
    del_field = form.old_field.data
    if form.validate_on_submit():  # extra_validators=None
        if request.method == "POST":
            if request.form["del_field_button"] == "Delete":
                # use form data to get the field to update
                field = Field.query.filter_by(subject=str(form.old_field.data).title()).first_or_404()
                db.session.delete(field)
                db.session.commit()
                flash("You have deleted the field", "success")
                return redirect(url_for("update_field"))
    return render_template("update_n_del_field.html", form=form, subjects=subjects,
                           grid_size=CONTENT_COL_2, del_field=del_field)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

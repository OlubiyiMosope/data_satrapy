from flask import render_template, url_for, flash, redirect, request
from data_satrapy import app, db, bcrypt
from data_satrapy.forms import RegistrationForm, LoginForm, PostForm
from data_satrapy.models import User, Post, Field
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template("home.html", home_active="active", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About", about_active="active")


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
    return render_template("register.html", title="Register", form=form, register_active="active")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        redirect(url_for("home"))
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
    return render_template("login.html", title="Login", form=form, login_active="active")


@app.route("/post_new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, field=1)
        db.session.add(post)
        db.session.commit()
        flash("Your new post has been created!", "success")
        return redirect(url_for("home"))
    return render_template("create_post.html", title="New Post", form=form,)


@app.route("/post")
def post():

    return render_template("post.html", )


@app.route("/logout")
def logout():
    logout_user()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("home"))

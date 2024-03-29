from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required
from data_satrapy import db, bcrypt, CONTENT_COL, CONTENT_COL_2
from data_satrapy.models import User
from data_satrapy.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                      RequestResetForm, ResetPasswordForm)
from data_satrapy.users.utils import send_reset_email, save_picture
from data_satrapy.main.utils import ordered_field_list, post_field_num


users = Blueprint('users', __name__)


@users.route("/admin_register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! You are now able to log in", "success")
        return redirect(url_for("main.home"))
    fields_list = ordered_field_list()
    return render_template("register.html", title="Register", form=form,
                           register_active="active", grid_size=CONTENT_COL,
                           fields_list=fields_list, post_field_num=post_field_num)


@users.route("/admin_login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # flash("You are already logged in.", "success")
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash("You have been logged in!", "success")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login unsuccessful! Please check username and password.", "danger")
    fields_list = ordered_field_list()
    return render_template("login.html", title="Login", form=form,
                           login_active="active", grid_size=CONTENT_COL,
                           fields_list=fields_list, post_field_num=post_field_num)


@users.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_img.data:
            picture_file = save_picture(form.profile_img.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='pics/' + current_user.image_file)
    fields_list = ordered_field_list()
    return render_template('account.html', title='Account', form=form, account_active="active",
                           image_file=image_file, grid_size=CONTENT_COL_2,
                           fields_list=fields_list, post_field_num=post_field_num)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    fields_list = ordered_field_list()
    return render_template('reset_request.html', title='Reset Password', form=form,
                           grid_size=CONTENT_COL_2,
                           fields_list=fields_list, post_field_num=post_field_num)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))

    fields_list = ordered_field_list()
    return render_template('reset_token.html', title='Reset Password',
                           form=form, grid_size=CONTENT_COL_2,
                           fields_list=fields_list, post_field_num=post_field_num)

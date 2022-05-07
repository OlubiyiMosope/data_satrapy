from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import login_required
from data_satrapy import db, CONTENT_COL_2
from data_satrapy.models import Field, Post
from data_satrapy.fields.forms import AddFieldForm, UpdateDeleteFieldForm
from data_satrapy.fields.utils import delete_field
from data_satrapy.main.utils import ordered_field_list, post_field_num


fields = Blueprint("fields", __name__)
# CONTENT_COL = 6
# CONTENT_COL_2 = 8


@fields.route("/field/", methods=["GET", "POST"])
@login_required
def add_field():
    form = AddFieldForm()
    if form.validate_on_submit():
        subject = str(form.post_subject.data).strip().title()
        # if not Field.query.filter_by(subject=subject).first():
        field = Field(subject=subject)
        db.session.add(field)
        db.session.commit()
        flash(f"New field '{field.subject}' has been added to database", "success")
        return redirect(url_for("fields.add_field"))  # to refresh the page

    fields_list = ordered_field_list()
    return render_template("add_field.html", title="Add Field", form=form,
                           add_field_active="active", grid_size=CONTENT_COL_2,
                           fields_list=fields_list, post_field_num=post_field_num)


@fields.route("/field/<string:field_name>")
def field_posts(field_name):
    page = request.args.get("page", 1, type=int)
    subject = Field.query.filter_by(subject=field_name).first_or_404()
    posts = Post.query.filter_by(field=subject)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)

    fields_list = ordered_field_list()
    return render_template("field_posts.html", title=field_name, subject=subject,
                           posts=posts, grid_size=CONTENT_COL_2,
                           fields_list=fields_list, post_field_num=post_field_num)


@fields.route("/field/<int:subject_id>/update", methods=["GET", "POST"])
@login_required
def update_field(subject_id):
    field = Field.query.get_or_404(subject_id)
    form = UpdateDeleteFieldForm()

    # if request.method == "POST":
    if request.form.get("delete") == "delete":
        delete_field(subject_id)
        return redirect(url_for("fields.add_field"))

    if form.validate_on_submit():
        field.subject = form.new_field.data.strip().title()
        db.session.commit()
        flash("You have successfully updated the field", "success")
        return redirect(url_for("fields.update_field", subject_id=subject_id))
    elif request.method == "GET":
        # form.old_field.data = field.subject
        form.new_field.data = field.subject

    fields_list = ordered_field_list()
    return render_template("update_n_del_field.html", title="Update/Delete Field",
                           form=form, grid_size=CONTENT_COL_2,
                           del_field=field.subject, current_field=field.subject,
                           fields_list=fields_list, post_field_num=post_field_num)

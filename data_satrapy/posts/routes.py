import os
from flask import (render_template, url_for, flash, redirect,
                   abort, request, current_app, Blueprint)
from flask_login import login_required, current_user
from data_satrapy import db, CONTENT_COL, CONTENT_COL_2
from data_satrapy.models import Post
from data_satrapy.posts.forms import PostForm
from data_satrapy.posts.utils import list_subs, save_picture, find_field, src_match
from data_satrapy.main.utils import ordered_field_list, post_field_num


posts = Blueprint("posts", __name__)


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    title = post.title.capitalize()
    fields_list = ordered_field_list()

    if post.nb_filename:
        if post.thumbnail:
            thumbnail_loc = url_for("static", filename="thumbnails/" + post.thumbnail)
        else:
            thumbnail_loc = ""

        if post.thumbnail_src:
            name, link = src_match(post.thumbnail_src)
        else:
            name, link = "", ""
        return render_template(f"nb_files/{post.nb_filename}", title=title, thumbnail_loc=thumbnail_loc,
                               post=post, name=name, link=link,)

    elif post.thumbnail and not post.nb_filename:
        thumbnail_loc = url_for("static", filename="thumbnails/" + post.thumbnail)

        if post.thumbnail_src:
            name, link = src_match(post.thumbnail_src)
        else:
            name, link = "", ""
        return render_template("post.html", title=title, post=post, name=name, link=link,
                               thumbnail_loc=thumbnail_loc, grid_size=CONTENT_COL_2,
                               fields_list=fields_list, post_field_num=post_field_num)

    return render_template("post.html", title=title, post=post,
                           grid_size=CONTENT_COL_2, fields_list=fields_list,
                           post_field_num=post_field_num)


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    options = list_subs()
    form.post_subject.choices = options

    # manually name thumbnail file
    all_posts = Post.query.all()
    # if there are no posts in the db, set the post_id to 1
    if len(all_posts) == 0:
        post_id = 1
    else:
        post_id = all_posts[-1].id + 1

    if form.validate_on_submit():
        field = find_field(form.post_subject.data)

        # These are nullable in the database.
        if form.thumbnail.data and form.thumbnail_src.data and form.nb_filename.data:
            filename = f"post-{post_id}"
            img_file = save_picture(form.thumbnail.data, filename)
            post = Post(title=form.title.data, content=form.content.data,
                        author=current_user, field_rel=field, nb_filename=form.nb_filename.data,
                        thumbnail=img_file, thumbnail_src=form.thumbnail_src.data)
            db.session.add(post)
            db.session.commit()
            flash("Your new post has been created!", "success")
        elif form.thumbnail.data and form.thumbnail_src.data:
            filename = f"post-{post_id}"
            img_file = save_picture(form.thumbnail.data, filename)
            post = Post(title=form.title.data, content=form.content.data,
                        author=current_user, field_rel=field,
                        thumbnail=img_file, thumbnail_src=form.thumbnail_src.data)
            db.session.add(post)
            db.session.commit()
            flash("Your new post has been created!", "success")
        elif form.nb_filename.data:
            post = Post(title=form.title.data, content=form.content.data,
                        author=current_user, field_rel=field, nb_filename=form.nb_filename.data)
            db.session.add(post)
            db.session.commit()
            flash("Your new post has been created!", "success")
        elif form.thumbnail.data and not form.thumbnail_src.data:
            flash("Your new post was not been created! Please add the thumbnail credit", "danger")
            return redirect(url_for("posts.new_post"))
        else:
            post = Post(title=form.title.data, content=form.content.data,
                        author=current_user, field_rel=field)
            db.session.add(post)
            db.session.commit()
            flash("Your new post has finally been created!", "success")
        return redirect(url_for("main.home"))

    return render_template("create_post.html", title="New Post", form=form,
                           new_post_active="active", src_match=src_match,
                           legend="Create A New Post", grid_size=CONTENT_COL)


@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    form = PostForm(post_subject=post.field_rel)
    options = list_subs()
    form.post_subject.choices = options
    if form.validate_on_submit():
        if form.thumbnail.data:
            # delete old thumbnail file if it exists
            if post.thumbnail:
                post_thumbnail = os.path.join(current_app.root_path, "static/thumbnails", post.thumbnail)
                if os.path.exists(post_thumbnail):
                    os.remove(post_thumbnail)
            filename = f"post-{post_id}"
            img_file = save_picture(form.thumbnail.data, filename)
            post.thumbnail = img_file
        if form.thumbnail_src:
            post.thumbnail_src = form.thumbnail_src.data
        if form.nb_filename.data:
            post.nb_filename = form.nb_filename.data
        post.title = form.title.data
        post.content = form.content.data
        post.field_rel = find_field(form.post_subject.data)
        db.session.commit()
        flash("Your post has been updated", "success")
        return redirect(url_for("posts.post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.thumbnail_src.data = post.thumbnail_src
        form.nb_filename.data = post.nb_filename

    return render_template("create_post.html", title="Update Post",
                           form=form, legend="Update Post", grid_size=CONTENT_COL)


@posts.route("/post/<int:post_id>/delete", methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", "success")
    return redirect(url_for("main.home"))

from flask import render_template, Blueprint
from flask_login import login_required
from data_satrapy.models import Field
from data_satrapy.posts.forms import DynamicPostForm
from data_satrapy import CONTENT_COL_2


posts = Blueprint("posts", __name__)


def list_subs():
    subs = [str(field) for field in Field.query.all()]
    subs.sort()
    return subs


@posts.route("/post")
def post():

    return render_template("post.html", title="Post", grid_size=CONTENT_COL_2)


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = DynamicPostForm()
    # QUERY DATABASE FOR SUBJECTS IN FIELD MODEL.
    subjects = Field.query.all()
    options = list_subs()
    form.post_subject.choices = options
    # if form.validate_on_submit():
    #     post = Post(title=form.title.data, content=form.content.data, author=current_user, field=1)
    #     db.session.add(post)
    #     db.session.commit()
    #     flash("Your new post has been created!", "success")
    #     return redirect(url_for("main.home"))
    return render_template("dynamic_post.html", title="New Post", form=form,
                           subjects=subjects, new_post_active="active",
                           grid_size=CONTENT_COL_2)

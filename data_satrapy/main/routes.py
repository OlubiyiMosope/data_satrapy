from flask import render_template, request, Blueprint
from data_satrapy.models import Post
from data_satrapy import CONTENT_COL


main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()). \
        paginate(page=page, per_page=5)
    return render_template("home.html", home_active="active", posts=posts,
                           grid_size=CONTENT_COL)


@main.route("/about")
def about():
    return render_template("about.html", title="About", about_active="active",
                           grid_size=CONTENT_COL)

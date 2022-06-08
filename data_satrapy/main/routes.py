from flask import render_template, request, url_for, Blueprint
from data_satrapy.models import Post
from data_satrapy.main.utils import ordered_field_list, post_field_num
from data_satrapy import CONTENT_COL, CONTENT_COL_2


main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()). \
        paginate(page=page, per_page=5)

    fields_list = ordered_field_list()
    return render_template("home.html", home_active="active", posts=posts, len=len,
                           grid_size=CONTENT_COL_2, fields_list=fields_list,
                           post_field_num=post_field_num)


@main.route("/about")
def about():
    avatar = "about_me_pic.PNG"
    about_me_pic = url_for("static", filename=f"pics/{avatar}")
    fields_list = ordered_field_list()
    return render_template("about.html", title="About", about_active="active",
                           grid_size=CONTENT_COL_2, about_me_pic=about_me_pic,
                           fields_list=fields_list, post_field_num=post_field_num)

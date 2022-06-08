from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import bleach
from markdown import markdown
from flask import current_app
from data_satrapy import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    posts = db.relationship("Post", backref="author", lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}',)"


class Field(db.Model):
    __tablename__ = "fields"
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(120), unique=True, nullable=False)
    posts = db.relationship("Post", backref="field_rel", lazy=True)

    def __repr__(self):
        return f"{self.subject}"


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text,)
    nb_filename = db.Column(db.String(120),)
    thumbnail = db.Column(db.String(20))
    thumbnail_src = db.Column(db.String(80))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey("fields.id"), nullable=False)  # default value for "others"

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", "code",
        "em", "i", "li", "ol", "pre", "strong", "ul", "div", "form", "img"
        "h1", "h2", "h3", "h4", "h5", "h6", "p", "button", "figure", "figcaption",
        "section", "kbd", "dl", "mark", "small", "u", "strike", "center", "font",
        "br", "hr", "table", "tr", "td", "th",]
        target.content_html = bleach.linkify(bleach.clean(
                                    markdown(value, output_format='html'),
                                    tags=allowed_tags, strip=True))

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.field_rel}', '{self.thumbnail}')"


db.event.listen(Post.content, 'set', Post.on_changed_body)

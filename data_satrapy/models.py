from datetime import datetime
from data_satrapy import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}',)"


class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(120), unique=True, nullable=False)  #
    fields = db.relationship("Post", backref="field", lazy=True)

    def __repr__(self):
        return f"{self.subject}"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey("field.id"), nullable=False)  # default value for "others"

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.field}', '{self.author}')"

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from data_satrapy.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
mail = Mail()

CONTENT_COL = 6
CONTENT_COL_2 = 8


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # with app.app_context():
    #     db.create_all()

    from data_satrapy.users.routes import users
    from data_satrapy.posts.routes import posts
    from data_satrapy.fields.routes import fields
    from data_satrapy.main.routes import main

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(fields)
    app.register_blueprint(main)

    return app

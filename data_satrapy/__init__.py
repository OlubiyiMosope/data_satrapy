from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_pagedown import PageDown
from data_satrapy.config import config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
pagedown = PageDown()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"

CONTENT_COL = 6
CONTENT_COL_2 = 7


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    with app.app_context():
        # db.create_all()

        from data_satrapy.users.routes import users
        from data_satrapy.posts.routes import posts
        from data_satrapy.fields.routes import fields
        from data_satrapy.main.routes import main
        from data_satrapy.errors.handlers import errors

        app.register_blueprint(users)
        app.register_blueprint(posts)
        app.register_blueprint(fields)
        app.register_blueprint(main)
        app.register_blueprint(errors)

        return app

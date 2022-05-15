import os
from flask_migrate import Migrate, upgrade
from data_satrapy import create_app, db
from data_satrapy.models import Post, User, Field

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Field=Field, Post=Post)


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()

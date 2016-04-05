from flask.ext.migrate import Migrate, MigrateCommand   # noqa
from beavy.app import app, db
import os

"""
Setup Migration and Database commands
"""

# and database migrations
migrate = Migrate(app, db)

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


@migrate.configure
def configure_alembic(config):
    paths = [os.path.join('migrations', 'versions')]
    app_migrations_path = os.path.join(BASE_DIR,
                                       'beavy_apps',
                                       app.config.get("APP"),
                                       'migrations')

    if os.path.isdir(app_migrations_path):
        paths.append(app_migrations_path)

    config.set_main_option('version_locations', " ".join(paths))
    return config

from sqlalchemy import MetaData
import os
import pytest
import sys


if os.environ.get("WITH_SQL", False):
    # SHOW all debug info of SQL streams
    import logging

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger = logging.getLogger('sqlalchemy.engine')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)

os.environ["BEAVY_ENV"] = "TEST"
from beavy.app import app, db
from beavy.commands.database import migrate
from flask.ext.migrate import upgrade as apply_migrations, downgrade

def pytest_cmdline_preparse(args):
    # we only mess if nothing else is supplied
    if args:
        return args

    args.insert(0, "-vv")
    args.append("tests")

    def add_path_with_coverage(x):
        args.append("--cov={}".format(x))
        args.append(x)

    args.extend(["--cov-config", ".coveragerc"])


    for module in app.config.get("MODULES", []):
        add_path_with_coverage("beavy_modules/{}".format(module))

    add_path_with_coverage("beavy_apps/{}".format(app.config["APP"]))


def pytest_runtest_call(item):
    # Flush all fixtures before the test is called
    if hasattr(item, 'funcargs') and 'db_session' in item.funcargs:
        item.funcargs.get('db_session').flush()


@pytest.yield_fixture(scope='session')
def testapp(request):
    """Session-wide test `Flask` application."""

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    try:
        yield app
    finally:
        ctx.pop()


@pytest.yield_fixture(scope="function")
def db_session(testapp):
    with testapp.app_context():
        apply_migrations()
        connection = db.engine.connect()
        transaction = connection.begin()
        session = db.create_scoped_session()
        db.session = session
        yield session
        transaction.rollback()
        connection.close()
        session.remove()

        db.drop_all()
        # Drop leftover tables (e.g. Alembic schema versions).
        md = MetaData()
        md.reflect(bind=db.engine)
        for table in md.sorted_tables:
            table.drop(db.engine)

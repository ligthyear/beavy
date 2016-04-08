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

@pytest.fixture(scope='session')
def testapp(request):
    """Session-wide test `Flask` application."""

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app

@pytest.fixture(scope='function')
def db_session(request):
    """Creates a new database session for a test."""
    db.create_all()

    connection = db.engine.connect()
    transaction = connection.begin()

    session = db.create_scoped_session(options=dict(bind=connection))

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()
        db.drop_all()

    request.addfinalizer(teardown)
    return session

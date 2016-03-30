import os
import pytest
import sys

os.environ["BEAVY_ENV"] = "TEST"
from beavy.app import app, db


def get_all_beavy_paths(fn):
    fn("beavy")

    for module in app.config.get("MODULES", []):
        fn("beavy_modules/{}".format(module))

    return fn("beavy_apps/{}".format(app.config["APP"]))


def pytest_cmdline_preparse(args):
    # we only mess if nothing else is supplied
    if args != ["beavy"]:
        return args

    args.insert(0, "-vv")

    def add_path_with_coverage(x):
        args.append("--cov={}".format(x))
        args.append(x)

    args.extend(["--cov-config", ".coveragerc"])

    get_all_beavy_paths(add_path_with_coverage)



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
    connection = db.engine.connect()
    db.create_all()
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

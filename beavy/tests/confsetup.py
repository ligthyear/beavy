from sqlalchemy import MetaData
import pytest
import sys

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

    add_path_with_coverage('beavy')

    for module in app.config.get("MODULES", []):
        add_path_with_coverage("beavy_modules/{}".format(module))

    add_path_with_coverage("beavy_apps/{}".format(app.config["APP"]))


def pytest_runtest_call(item):
    # Flush all fixtures before the test is called
    if hasattr(item, 'funcargs') and 'db_session' in item.funcargs:
        item.funcargs.get('db_session').flush()


@pytest.yield_fixture(scope='function')
def authed_client(testapp, db_session):
    from beavy.models.login import Login
    from beavy.models.persona import Person

    login = Login(persona=Person(), provider="test", profile_id="test")
    db_session.add(login)
    db_session.commit()

    with testapp.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = login.id
            sess['_fresh'] = True

        c.login = login
        yield c



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

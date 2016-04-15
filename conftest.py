import os

if os.environ.get("WITH_SQL", False):
    # SHOW all debug info of SQL streams
    import logging

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)-5.5s [%(name)s] \n %(message)s\n ----'))

    logger = logging.getLogger('sqlalchemy.engine')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)

os.environ["BEAVY_ENV"] = "TEST"

from beavy.tests.confsetup import *   # noqa

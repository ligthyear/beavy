from flask.ext.script import Manager
from beavy.app import app as beavy

from .user import UserCommand
from .database import MigrateCommand
from .app import AppCommand

"""
The entry point for manager.py commands
"""

# FIXME: add support to allow modules and apps to ship commands


manager = Manager(beavy)

manager.add_command("user", UserCommand)
manager.add_command("db", MigrateCommand)
manager.add_command("app", AppCommand)

try:
    # conditionally, if we have behave setup
    from .behve import BehaveCommand     # noqa
    manager.add_command("behave", BehaveCommand)
except ImportError:
    pass


# and general commands

from flask.ext.script import Command, Option
from behave.configuration import options as behave_options
from behave.__main__ import main as behave_main

from beavy.app import app

import os
import sys


class BehaveCommand(Command):

    def get_options(self):
        res = []
        for args, kwargs in behave_options:
            if not args:
                continue
            if "config_help" in kwargs:
                del kwargs['config_help']
            res.append(Option(*args, **kwargs))
        return res

    def run(self, *args, **kwargs):
        frontend = os.environ.get("APP", app.config.get("APP", None))
        if not frontend:
            print("You need to configure the APP to be used!")
            exit(1)

        exit(behave_main(sys.argv[2:] + ['--no-capture',
             "beavy_apps/{}/tests/features".format(frontend)]))

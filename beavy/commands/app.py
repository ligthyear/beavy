from flask_script import Manager
from beavy.app import app

import os
import re

AppCommand = Manager(usage="app management")


@AppCommand.command
def paths():
    return ""
    results = ["beavy"]

    for module in app.config.get("MODULES", []):
        results.append("beavy_modules/{}".format(module))

    results.append("beavy_apps/{}".format(app.config["APP"]))

    print(" ".join(results))


@AppCommand.command
def create(name):
    """
    Setup beavy template and infrastructure for a new app
    given the @name.
    """
    ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..")

    if not re.match("^[a-z][a-z0-9]{2,24}$", name):
        print("""Sorry, the app name has to be a lower-cased 3-25 character
long string only containing letters, numbers and underscore and starting
with a letter!""")
        print("RegEx: ^[a-z][a-z0-9]{2,24}$ ")
        exit(1)

    APP_DIR = os.path.join(ROOT_DIR, "beavy_apps", name)

    if os.path.exists(APP_DIR):
        print("{} directory already exists. Exiting.".format(name))
        exit(1)

    # minimal setup
    os.mkdir(APP_DIR)
    open(os.path.join(APP_DIR, "__init__.py"), 'w').close()

    # create minimal frontend
    os.mkdir(os.path.join(APP_DIR, "frontend"))

    with open(os.path.join(APP_DIR, "frontend",
                           "application.jsx"), 'w') as jsx:
        jsx.write("""
import React from "react";
import { MainMenu } from "components/MainMenu";
import UserModal from "containers/UserModal";
import UserMenuWidget from "containers/UserMenuWidget";

import { getExtensions } from "config/extensions";

// This is your app entry point
export default class Application extends React.Component {
    render() {
        return <div>
                  <UserModal />
                  <MainMenu
                    logo='http://beavy.xyz/logos/logo.svg'
                    navigationTools={<UserMenuWidget />}
                  >
                    {getExtensions('MainMenuItem').map(x=>x.call(this))}
                  </MainMenu>
                  {this.props.children}
                </div>;
    }
}

""")

    # create testing infrastructure
    os.mkdir(os.path.join(APP_DIR, "tests"))

    with open(os.path.join(APP_DIR, "tests", "environment.py"), 'w') as env:
        env.write("from beavy.testing.environment import *\n")

    os.mkdir(os.path.join(APP_DIR, "tests", "steps"))

    with open(os.path.join(APP_DIR, "tests", "steps", "steps.py"), 'w') as stp:
        stp.write("from beavy.testing.steps import *\n")

    print("{} successfully created!".format(name))

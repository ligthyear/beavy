from flask import Blueprint

user_bp = Blueprint('users', 'beavy.users')
account_bp = Blueprint('account', 'beavy.account')
object_bp = Blueprint('object', 'beavy.object')
activity_bp = Blueprint('activity', 'beavy.activity')
lists_bp = Blueprint('lists', 'beavy.lists')

# Deprecated – Legacy support
users = user_bp
account = account_bp
obj = object_bp
activity = activity_bp


def setup(app):
    URLS = app.config["URLS"]
    app.register_blueprint(user_bp,
                           url_prefix=URLS["USERS"])
    app.register_blueprint(account_bp,
                           url_prefix=URLS['ACCOUNT'])
    app.register_blueprint(object_bp,
                           url_prefix=URLS['OBJECT'])
    app.register_blueprint(activity_bp,
                           url_prefix=URLS['ACTIVITY'])
    app.register_blueprint(lists_bp,
                           url_prefix=URLS['LIST'])

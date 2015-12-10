from beavy.common.admin_model_view import AdminPolyModelView
from beavy.app import admin, db

from .models import Topic
from .blueprint import hive_bp
from .models import *  # noqa
from .views import *  # noqa


def init_app(app):

    app.register_blueprint(hive_bp)
    admin.add_view(AdminPolyModelView(Topic, db.session,
                                      name="Topics",
                                      menu_icon_type='glyph',
                                      menu_icon_value='glyphicon-file'))

from beavy.app import app
from beavy.models.object import Object
from beavy.schemas.object import ObjectField


def models_comments_active_list():
    if not hasattr(models_comments_active_list, "__cache"):

        try:
            items = app.config.get("Comments", {})["on"]
        except KeyError:
            items = Object.__mapper__.polymorphic_map.keys()

        models_comments_active_list.__cache = items

    return models_comments_active_list.__cache


def get_object_model(key):
    return Object.__mapper__.polymorphic_map[key]


def get_object_schema(key):
    return ObjectField.registry[key]

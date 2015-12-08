from .utils import (models_comments_active_list,
                    get_object_model,
                    get_object_schema)
from beavy.common.payload_property import PayloadProperty
from marshmallow_jsonapi import fields


def patch_models():
    for model_name in models_comments_active_list():
        try:
            model_cls = get_object_model(model_name)
        except KeyError:
            print("Can't activate on {} – model not found".format(model_name))
            continue

        model_cls.comments_count = PayloadProperty('comments_count')

        try:
            object_schema = get_object_schema(model_name)
        except KeyError:
            print("Can't activate on {} – schema not found".format(model_name))
            continue

        object_schema._declared_fields["comments_count"] = fields.Integer(default=0)


def setup():
    patch_models()

from beavy.common.paging_schema import makePaginationSchema
from beavy.common.morphing_schema import MorphingSchema
from marshmallow_jsonapi import Schema, fields

from collections import namedtuple

dumpObj = namedtuple('MarshmallowDump', 'data error')

from .user import BaseUser


class BaseObject(Schema):
    class Meta:
        type_ = "object"

    id = fields.Integer()
    created_at = fields.DateTime()
    owner = fields.Nested(BaseUser)
    belongs_to_id = fields.Integer()  # don't leak
    type = fields.String(attribute="discriminator")


class ObjectField(MorphingSchema):
    FALLBACK = BaseObject
    registry = {}


class ObjectSchema(ObjectField, BaseObject):

    def dump(self, value, many=False, **kwargs):
        if many:
            return dumpObj([self._get_serializer(x).dump(x).data
                            for x in value], {})
        return dumpObj(self._get_serializer(value).dump(value), {})

objects_paged = makePaginationSchema(ObjectSchema)()

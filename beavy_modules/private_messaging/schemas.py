from beavy.common.paging_schema import makePaginationSchema
from beavy.schemas.object import ObjectField
# , Schema, fields
from marshmallow_jsonapi import Schema, fields

from .models import PM_ID


class PrivateMessageSchema(Schema):
    id = fields.Integer()
    created_at = fields.DateTime()
    title = fields.String()
    type = fields.String(attribute="discriminator")

    class Meta:
        type_ = 'private_message'  # Required


pm = PrivateMessageSchema()
pm_paged = makePaginationSchema(PrivateMessageSchema)()

ObjectField.registry[PM_ID] = PrivateMessageSchema

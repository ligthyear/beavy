from marshmallow import pre_dump, Schema, fields


class PickBestImageField(fields.Field):

    def _serialize(self, images, attr, obj):
        if not images:
            return None
        return images[0]["src"]


class BriefLinkSchema(Schema):

    url = fields.URL()
    title = fields.String()
    description = fields.String()
    type = fields.String()
    images = PickBestImageField(dump_to="image_url")

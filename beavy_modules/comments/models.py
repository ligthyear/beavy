from beavy.models.object import Object
from flask_security.core import current_user
from sqlalchemy.sql import and_
from beavy.common.rendered_text_mixin import RenderedTextMixin
from sqlalchemy.orm import validates
from beavy.app import db
from .utils import models_comments_active_list

COMMENT_ID = "comment"


class CommentObject(Object, RenderedTextMixin):
    __mapper_args__ = {
        'polymorphic_identity': COMMENT_ID
    }

    CAPABILITIES = [Object.Capabilities.listed_for_activity]

    in_reply_to_id = db.Column(db.Integer, db.ForeignKey("objects.id"),
                               nullable=True)
    # in_reply_to = db.relationship(Object, backref=db.backref('replies'))

    @validates('belongs_to')
    def validate_belongs_to(self, key, value):
        assert value is not None, "specify the object this comments belongs to"

        obj = Object.query.get(value)
        assert obj is not None, "object specified not found"

        assert obj.type in models_comments_active_list(), \
            "Not configured to allow comments on '{}' object".format(obj.type)

        return value


def filter_comments_for_view(cls, method):
    if not current_user or current_user.is_anonymous:
        return
    return and_(cls.discriminator == COMMENT_ID,
                cls.owner_id == current_user.id)

Object.__access_filters['view'].append(filter_comments_for_view)

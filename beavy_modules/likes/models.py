from beavy.models.activity import Activity
from beavy.models.object import Object
from beavy.common.payload_property import PayloadProperty
from datetime import datetime
from sqlalchemy import event

LIKE_ID = 'like'


class Like(Activity):
    __mapper_args__ = {
        'polymorphic_identity': LIKE_ID
    }


Object.likes_count = PayloadProperty('{}s.count'.format(LIKE_ID), default=0)
Object.likes_updated = PayloadProperty('{}s.updated'.format(LIKE_ID))


def update_object_likes_count(mapper, connection, target):
    # unfortunately, we can't do an aggregate in update directly...
    # TODO: it would be nice if we could _only_ update our items
    # instead of the entire payload
    obj = target.object
    obj.likes_count = Like.query.filter(
        Like.object_id == obj.id).count()
    obj.likes_updated = datetime.now().isoformat()

    Object.query.filter(
        Object.id == target.object_id
        ).update(dict(payload=obj.payload))


event.listen(Like, 'after_insert', update_object_likes_count)
event.listen(Like, 'after_delete', update_object_likes_count)

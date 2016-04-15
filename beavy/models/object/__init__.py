from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import contains_eager, aliased
from enum import Enum, unique
from sqlalchemy import func
from flask.ext.security import current_user
from beavy.common.access_query import AccessQuery
from itertools import chain
from flask import abort

from ..persona import Persona
from beavy.app import db
from collections import defaultdict


class ObjectQuery(AccessQuery):

    def by_capability(self, aborting=True, abort_code=404, *caps):
        caps = set(chain.from_iterable(map(lambda c:
                                           getattr(Object.TypesForCapability,
                                                   getattr(c, 'value', c), []),
                                           caps)))
        if not caps:
            # No types found, break right here.
            if aborting:
                raise abort(abort_code)
            return self.filter("1=0")

        return self.filter(Object.discriminator.in_(caps))

    def with_my_activities(self):
        if not current_user or not current_user.is_authenticated:
            return self

        from ..activity import Activity

        my_activities = aliased(Activity.query.filter(
            Activity.subject_id == current_user.id
            ).cte(name="my_activities"), "my_activities")

        return self.outerjoin(my_activities).options(contains_eager(
            Object.my_activities, alias=my_activities))


class SharedWith(db.Model):
    __table__ = db.Table('object_shared', db.metadata,
                         db.Column('object_id',
                                   db.Integer(),
                                   db.ForeignKey("objects.id"),
                                   nullable=False),
                         db.Column('persona_id',
                                   db.Integer(),
                                   db.ForeignKey("persona.id"),
                                   nullable=False),
                         db.Column('level',
                                   db.String(20),
                                   nullable=False),
                         db.PrimaryKeyConstraint('object_id', 'persona_id'),
                         db.UniqueConstraint('object_id', 'persona_id')
                         )


class Object(db.Model):
    """
    This is the primary base class for all kind of objects
    we know of inside the system
    """
    @unique
    class Capabilities(Enum):
        # This type is to be shown in default lists
        # like 'top', 'latest' etc
        listed = 'listed'

        # If the type isn't listed but has `listed_for_activity`
        # it can show up in lists about activitys, for example
        # when an object got liked
        listed_for_activity = 'a_listable'

        # This can be searched for
        searchable = 'searchable'

    __tablename__ = "objects"
    query_class = ObjectQuery

    id = db.Column(db.Integer, primary_key=True)
    discriminator = db.Column('type', db.String(100), nullable=False)
    created_at = db.Column('created_at', db.DateTime(), nullable=False,
                           server_default=func.now())
    payload = db.Column('payload', JSONB, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(Persona.id), nullable=False)
    belongs_to_id = db.Column(db.Integer, db.ForeignKey("objects.id"),
                              nullable=True)

    public = db.Column('public', db.Boolean, nullable=False, default=False)

    __mapper_args__ = {'polymorphic_on': discriminator}

    owner = db.relationship(Persona, foreign_keys=owner_id)
    belongs_to = db.relationship("Object", foreign_keys=belongs_to_id)
    shared_with = db.relationship(SharedWith, lazy='dynamic')

    def share_with(self, persona, level="view"):
        sWith = self.shared_with.filter_by(persona_id=persona.id).first()
        if not sWith:
            sWith = SharedWith(persona_id=persona.id)
            self.shared_with.append(sWith)
        sWith.level = level
        return sWith

    def unshare_with(self, persona):
        self.shared_with.filter_by(persona_id=persona.id).delete()

Object.__access_filters = defaultdict(list)

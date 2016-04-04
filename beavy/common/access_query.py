from flask.ext.sqlalchemy import BaseQuery
from flask.ext.security import current_user
from flask import has_request_context
from sqlalchemy.sql import text, or_


class AccessQuery(BaseQuery):

    PUBLIC_SQL = """(
            public=true
        AND
            belongs_to_id IS NULL
    )"""

    def _gen_filters(self, class_, fltr):
        return [x for x in filter(lambda x: x is not None, [
            t(class_, fltr)
            # weirdly class_.__access_filters fails on us
            # probably some sqlalchemy magic
            for t in getattr(class_, "__access_filters")[fltr]]
            )
        ]

    @property
    def accessible(self):
        if not has_request_context() or not current_user.is_authenticated:
            return self.filter(text(self.PUBLIC_SQL))

        return self.filter(text("""{} OR (
            owner_id =:__owner_id
            OR
            owner_id in (SELECT target_id from persona_roles
                            where source_id = :__owner_id)
        )""".format(self.PUBLIC_SQL))
            ).params(__owner_id=current_user.current_persona.id)

    def filter_visible(self, attr, remoteAttr):
        filters = self._gen_filters(remoteAttr.class_, 'view')
        if not filters:
            return self.accessible

        return self.accessible.filter(attr.in_(
            remoteAttr.class_.query.filter(or_(*filters))
                             .with_entities(remoteAttr)
                             .subquery()
            )
        )

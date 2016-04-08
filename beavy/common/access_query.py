from flask.ext.sqlalchemy import BaseQuery
from flask.ext.security import current_user
from flask import has_request_context
from sqlalchemy.sql import text, or_, select


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


        # top_query = Role.query.filter(Role.source_id == self.id
        #                               ).cte(name="persona_graph",
        #                                     recursive=True)
        #
        # top_aliased = top_query.alias()
        # return top_query.union(Role.query.join(top_aliased,
        #                        Role.source_id == top_aliased.c.target_id))

    def _items_subquery(self, persona):
        persona_graph = persona.persona_graph
        slc = self._primary_entity.selectable

        from beavy.app import db

        print(db.session.query(persona_graph.c.target_id).all())
        print(db.session.query(slc.c.owner_id).all())
        print(db.session.query(slc.c.owner_id.in_(select([persona_graph.c.target_id]))).all())

        return slc.select().where(or_(
            text(self.PUBLIC_SQL), or_(
                slc.c.owner_id == persona.id, slc.c.owner_id.in_(select([persona_graph.c.target_id]))
            ))).cte(name="accessible_items_graph", recursive=True)
        top_aliased = top_query.alias()
        two = slc.select().select_from(slc.join(
            top_aliased, slc.c.belongs_to_id == top_aliased.c.id))
        unioned = top_query.union(two)
        print(db.session.query(unioned.c.id).all())
        return unioned

    @property
    def accessible(self):
        if not has_request_context() or not current_user.is_authenticated:
            return self.filter(text(self.PUBLIC_SQL))

        return self.filter(self._primary_entity.selectable.c.id.in_(select([self._items_subquery(current_user.current_persona).c.id])))

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

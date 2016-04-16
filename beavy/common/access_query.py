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

    def _items_subquery(self, persona):
        persona_graph = persona.persona_graph
        slc = self._primary_entity.selectable

        tests = [
            slc.c.owner_id == persona.id,
            slc.c.owner_id.in_(select([persona_graph.c.target_id]))
            ]

        try:
            swith = self._primary_entity.mapper.relationships["shared_with"].table
        except KeyError:
            pass
        else:
            tests.append(slc.c.id.in_(select([swith.c.object_id]
                         ).where(or_(swith.c.persona_id == persona.id, swith.c.persona_id.in_(
                                 select([persona_graph.c.target_id]))))))

        top_query = slc.select().where(or_(
            text(self.PUBLIC_SQL), or_(*tests
            ))).cte(name="accessible_items_graph", recursive=True)
        top_aliased = top_query.alias()
        two = slc.select().select_from(slc.join(
            top_aliased, slc.c.belongs_to_id == top_aliased.c.id)
            ).where(slc.c.public == True)
        return top_query.union(two)

    @property
    def accessible(self):
        return self.accessibility_query(current_user.current_persona if current_user.is_authenticated else None)

    def accessibility_query(self, persona):
        if not has_request_context() or not persona:
            return self.filter(text(self.PUBLIC_SQL))

        return self.filter(self._primary_entity.selectable.c.id.in_(select([self._items_subquery(persona).c.id])))

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

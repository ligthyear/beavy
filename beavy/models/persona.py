from sqlalchemy import func
from beavy.app import db


class Role(db.Model):
    __table__ = db.Table('persona_roles', db.metadata,
                         db.Column('source_id',
                                   db.Integer(),
                                   db.ForeignKey("persona.id"),
                                   nullable=False),
                         db.Column('target_id',
                                   db.Integer(),
                                   db.ForeignKey("persona.id"),
                                   nullable=False),
                         db.Column('role',
                                   db.String(20),
                                   nullable=False),
                         db.PrimaryKeyConstraint('source_id', 'target_id'),
                         db.UniqueConstraint('source_id', 'target_id')
                         )

    @property
    def name(self):
        return self.role


class Persona(db.Model):
    """
    An abstracted Actor in our system. Can be a natural Person, an Organisation
    an automatised bot or any other type of actor we might come up with in the
    future.

    A person is the entity acting upon object. Any object in our system must be
    owned by some Persona.
    """

    __tablename__ = "persona"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column('name', db.String(25), nullable=True, unique=True)
    pretty_name = db.Column('pretty_name', db.String(100), nullable=True)
    discriminator = db.Column('type', db.String(100), nullable=False)
    created_at = db.Column('created_at', db.DateTime(), nullable=False,
                           server_default=func.now())

    __mapper_args__ = {'polymorphic_on': discriminator}

    personas = db.relationship("Persona", secondary=Role.__table__,
                               backref="accessors",
                               primaryjoin=id == Role.__table__.c.source_id,
                               secondaryjoin=id == Role.__table__.c.target_id)

    @property
    def persona_graph(self):
        """
        Return a CTE query, which selects all personas and roles the
        persona can act as.
        """

        # Unfortunately it appears sqlalchemy doesn't allow recursive CTE
        # for FROM-AS-TEXT-Clause selects (as of v 1.0.12):
        # https://github.com/zzzeek/sqlalchemy/blob/master/test/sql/test_cte.py
        # for the record, this was the starting SQL we used:
        # ORIGINAL_SQL = """
        #   -- Initial Records
        #     SELECT pr.source_id,
        #            pr.target_id,
        #            pr.role
        #       FROM persona_roles pr
        #       WHERE pr.source_id = :__persona_id
        #   UNION
        #   -- Recursive Term
        #     SELECT pr.source_id,
        #            pr.target_id,
        #            pr.role
        #       FROM persona_roles as pr
        #       JOIN persona_graph as pg
        #         ON (pg.target_id = pr.source_id)
        # """).bindparams(__persona_id=self.id
        #    ).columns(source_id=db.Integer, target_id=db.Integer,
        #              role=db.String
        #    ).cte("persona_graph", recursive=True)
        #

        top_query = Role.query.filter(Role.source_id == self.id
                                      ).cte(name="persona_graph",
                                            recursive=True)

        top_aliased = top_query.alias()
        return top_query.union(Role.query.join(top_aliased,
                               Role.source_id == top_aliased.c.target_id))

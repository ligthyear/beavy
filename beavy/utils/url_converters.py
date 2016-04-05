from sqlalchemy.sql import or_
from flask import abort
from werkzeug.routing import BaseConverter
from ..models.persona import Persona
from ..models.activity import Activity
from ..models.object import Object


class ModelConverter(BaseConverter):
    __OBJECTS__ = {
        'persona': Persona,
        'object': Object,
        'activity': Activity
    }

    def __init__(self, url_map, obj="object"):
        super(ModelConverter, self).__init__(url_map)
        # match ID or string
        self.regex = '-?\d+|\S+'
        self.cls = self.__OBJECTS__[obj]

    def to_python(self, value):
        cls = self.cls
        try:
            return cls.query.get_or_404(int(value))
        except ValueError:
            pass

        if not getattr(cls, "__LOOKUP_ATTRS__", False):
            abort(404)

        return cls.query.filter(or_(*[getattr(cls, key) == value
                                      for key in cls.__LOOKUP_ATTRS__])
                                ).first_or_404()


class PersonaConverter(ModelConverter):

    def __init__(self, url_map):
        super(PersonaConverter, self).__init__(url_map, obj="persona")

from marshmallow import pre_dump


class MorphingSchema():

    @pre_dump
    def select_processor(self, obj, many=False,
                         strict=False, update_fields=False):
        if many:
            return [self._get_serializer(item) for item in obj]
        return self._get_serializer(obj)

    def _get_serializer(self, obj):
        name = obj.__mapper__.polymorphic_identity
        return self.registry.get(name, self.FALLBACK)()

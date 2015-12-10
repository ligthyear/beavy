from beavy.common.payload_property import PayloadProperty
from .tasks import extract_for_model


class LinkExtractionModelMixin():

    link_meta = PayloadProperty("__url_extractor_meta")

    @property
    def link_source(self):
        raise NotImplementedError("You need to return a unicode string here")

    def schedule_link_extraction(self):
        return extract_for_model.delay(self.id)

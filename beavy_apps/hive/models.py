from beavy.models.object import Object
from beavy.common.rendered_text_mixin import RenderedTextMixin
from beavy.common.payload_property import PayloadProperty
from beavy_modules.url_extractor.mixins import LinkExtractionModelMixin

TOPIC_ID = "topic"


class Topic(Object, RenderedTextMixin, LinkExtractionModelMixin):
    __mapper_args__ = {
        'polymorphic_identity': TOPIC_ID
    }

    title = PayloadProperty('title')
    text = PayloadProperty('text')
    url = PayloadProperty('url')

    @property
    def link_source(self):
        return self.url

    CAPABILITIES = [Object.Capabilities.listed, Object.Capabilities.searchable]

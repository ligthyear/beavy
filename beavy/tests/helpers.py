from beavy.models.object import Object

import json
import pytest

class TestObject(Object):
    __mapper_args__ = {
        'polymorphic_identity': "__helpers__test"
    }


def api_call(client, url, expected_code=200, method="get", **kwargs):
    if not "headers" in kwargs:
        kwargs['headers'] = [('Accept', 'application/vnd.api+json')]
    else:
        kwargs['headers'].append(('Accept', 'application/vnd.api+json'))

    resp = getattr(client, method)(url, **kwargs)

    if expected_code:
        assert resp.status_code == expected_code, "Wrong Status Code. Got {} expected {}".format(resp.status_code, expected_code)

    return json.loads(resp.get_data(as_text=True))

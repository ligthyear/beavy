from beavy.models.object import Object
from beavy.models.persona import Person
from .helpers import TestObject
from werkzeug.exceptions import NotFound, InternalServerError
import pytest

from enum import Enum, unique


@unique
class NonExistingCaps(Enum):
    is_not_there = "simply_isnt_there"


def test_faulty_capabilities_access(testapp, ListedTestObject, db_session):

    with pytest.raises(NotFound):
        Object.query.by_capability(NonExistingCaps.is_not_there)

    with pytest.raises(InternalServerError):
        Object.query.by_capability(NonExistingCaps.is_not_there,
            abort_code=500)

    assert Object.query.by_capability(NonExistingCaps.is_not_there,
        aborting=False).count() == 0


def test_capabilities_access(testapp, ListedTestObject, db_session):
    db_session.add(TestObject(owner=Person()))
    db_session.add(TestObject(owner=Person()))
    db_session.commit()

    assert Object.query.by_capability(Object.Capabilities.listed
            ).count() == 0

    db_session.add(ListedTestObject(owner=Person()))
    db_session.add(ListedTestObject(owner=Person()))
    db_session.add(ListedTestObject(owner=Person()))
    db_session.add(ListedTestObject(owner=Person()))
    db_session.add(ListedTestObject(owner=Person()))
    db_session.commit()

    assert Object.query.by_capability(Object.Capabilities.listed
        ).count() == 5
    assert Object.query.by_capability(Object.Capabilities.listed_for_activity
        ).count() == 5
    assert Object.query.by_capability(Object.Capabilities.listed,
                                      Object.Capabilities.listed_for_activity
        ).count() == 5

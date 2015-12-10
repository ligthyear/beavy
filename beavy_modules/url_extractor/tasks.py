from beavy.app import celery, db
from beavy.models.object import Object
from .lib import extract_info


@celery.task
def extract_for_model(model_id, cls=Object):
    model = db.session.query(cls).get(model_id)
    model.link_meta = extract_info(model.link_source)
    db.session.add(model)
    db.session.commit()

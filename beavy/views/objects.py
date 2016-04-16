from beavy.blueprints import object_bp
from beavy.utils import api_only
from beavy.models.object import External
from beavy.models.activity import Visited
from flask import redirect, url_for
from flask.ext.security import login_required, current_user
from beavy.app import db


@object_bp.route("/<model:object>/visited")
@login_required
@api_only
def visited(object):
    return {"visited": Visited.query.filter_by(
        subject_id=current_user.current_persona.id,
        object_id=object.id
        ).first() is not None}


@object_bp.route("/<model:object>/visit")
@login_required
@api_only
def visit(object):
    db.session.add(Visited(
        subject_id=current_user.current_persona.id,
        object_id=object.id))
    db.session.commit()
    return {"visited": True}


@object_bp.route("/<model:object>/external")
@login_required
def external(object):
    if isinstance(object, External):
        db.session.add(Visited(
            subject_id=current_user.current_persona.id,
            object_id=object.id))
        db.session.commit()
        return redirect(object.payload['link'])
    else:
        return redirect(url_for('object', object=object.id))

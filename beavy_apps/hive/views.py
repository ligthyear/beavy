from flask import request, abort
from beavy.app import db, current_user
from beavy.utils import fallbackRender
from flask.ext.security import login_required

from .blueprint import hive_bp
from .models import Topic
from .schemas import topic as topic_schema


@hive_bp.route("/t/<model:topic>/")
# FIXME: have an actual template
@fallbackRender('hacker_news/submit.html')
def show_topic(topic):
    return topic_schema.dump(topic)


@hive_bp.route("/submit/", methods=["GET", "POST"])
@fallbackRender('hello.html')
@login_required
def submit_story():
    if request.method == "POST":
        params = request.get_json()
        title, url = params['title'].strip(), params['url'].strip()
        text = params.get('text', "").strip()
        if not title:
            return abort(400, "You have to provide a 'title'")

        if not url and not text:
            return abort(400, "You have to provide at least 'url' or 'text', too")

        topic = Topic(title=title,
                      text=text,
                      url=url,
                      owner_id=current_user.id)
        db.session.add(topic)
        db.session.commit()
        return topic_schema.dump(topic)

    # Just render it
    return {}

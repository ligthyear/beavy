from flask.ext.security import SQLAlchemyUserDatastore
from flask import _request_ctx_stack


class UserStore(SQLAlchemyUserDatastore):

    def reload_user(self, *args, **kwargs):
        from beavy.utils.db_helpers import set_db_persona    # noqa
        # if we reload with a new user, we reflect that in the database
        ctx = _request_ctx_stack.top
        user_before = getattr(ctx, 'user', None)
        ret = super(UserStore, self).reload_user(*args, **kwargs)
        user_after = getattr(ctx, 'user', None)
        if user_after and user_after is not user_before:
            set_db_persona(user_after.current_persona)
        return ret

    def find_role(self, *args, **kwargs):
        """We don't do roles that way."""
        raise NotImplementedError

    def put(self, model):
        self.db.session.add(model, model.persona)
        return model

    def find_user(self, email=None, **kwargs):
        if email and not kwargs:
            # we are looking for email only, that is a special provider
            return self.user_model.query.filter_by(provider="email",
                                                   provider_id=email).first()
        return self.user_model.query.filter_by(**kwargs).first()

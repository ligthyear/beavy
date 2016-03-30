from flask.ext.security import SQLAlchemyUserDatastore


class UserStore(SQLAlchemyUserDatastore):

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

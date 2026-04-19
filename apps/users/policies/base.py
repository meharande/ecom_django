class Policy:
    def has_permission(self, user, action, resource=None, context=None):
        raise NotImplementedError

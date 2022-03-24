class Resource:
    def __init__(self, resource=None) -> None:
        super().__init__()
        self.resource = resource

    def configure(self, service):
        pass

    def resources(self):
        if not self.resource:
            return []

        return [self.resource]

    def permissions(self):
        return []

    def variables(self):
        return {}

    def enable_read(self, builder: "PolicyBuilder"):
        raise NotImplemented()

    def enable_write(self, builder: "PolicyBuilder"):
        raise NotImplemented()

    def enable_delete(self, builder: "PolicyBuilder"):
        raise NotImplemented()

    def get_att(self, name, as_dict=True):
        attr = self.resource.get_att(name)

        if not as_dict:
            return attr

        return attr.to_dict()


class DummyResource:
    def __init__(self, title, **kwargs):
        self.title = title
        self.kwargs = kwargs

    def to_dict(self):
        return self.kwargs

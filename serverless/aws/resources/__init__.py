class Resource:
    def configure(self, service):
        pass

    def resources(self):
        return []

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

class IStore:
    def fetch(self, locator):
        raise NotImplementedError("fetch")
    def store(self, data):
        raise NotImplementedError("store")

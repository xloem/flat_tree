class IStore:
    def fetch(self, locator):
        raise NotImplementedError("fetch")
    def store_index(self, index):
        return self.store_data(index)
    def store_data(self, data):
        raise NotImplementedError("store_data")

class ListStore(IStore):
    def __init__(self, list = []):
        self.list = list
    def fetch(self, locator):
        return self.list[int(locator)]
    def store_data(self, data):
        self.list.append(data)
        return str(len(self.list) - 1)

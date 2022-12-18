from . import mix_indices_oo, mix_indices, append_indices

__version__ = '0.1.0'

class flat_tree_append_indices:
    def __init__(self, storage, degree = 2, locator = None):
        self.storage = storage
        self.locator = locator
        if self.locator is not None:
            indices = self.storage.fetch(locator)
        else:
            indices = []
        self.indices = append_indices.append_indices(degree, indices)
    def append(self, added_size, added_data_locator):
        # append() could also take an out object and write to that, so as to not overwrite the local index until the upload succeeds
        self.indices.append(self.locator, added_size, added_data_locator)
        self.locator = self.storage.store_index(self.indices)
    def snap(self):
        return [*self]
    @property
    def leaf_count(self):
        return self.indices.leaf_count
    @property
    def byte_count(self):
        return self.indicesobj.size
    def __str__(self):
        return str(self.snap())
    def __iter__(self):
        return iter(self.indices)

class flat_tree_mix_indices(flat_tree_append_indices):
    def __init__(self, degree = 2, initial_indices = []):
        self.obj = mix_indices.append_indices(
            degree, [
                (leaf_count, offset, size, value)
                for leaf_count, value, offset, size
                in initial_indices
            ]
        )
    def __iter__(self):
        return (
            (leaf_count, value, offset, size)
            for leaf_count, offset, size, value
            in self.obj
        )

class flat_tree_mix_indices_oo:
    def __init__(self, degree = 2, initial_indices = []):
        self.obj = mix_indices_oo.index_node(
            degree, [
                (leaf_count, offset, size, value)
                for leaf_count, value, offset, size
                in initial_indices
            ]
        )
    def append(self, last_snap_locator, added_size, added_data_locator):
        self.obj.append(last_snap_locator, added_size, added_data_locator)
    def snap(self):
        return [*self]
    @property
    def leaf_count(self):
        return self.obj.leaf_count
    @property
    def byte_count(self):
        return self.obj.size
    def __str__(self):
        return str(self.snap())
    def __iter__(self):
        return (
            (leaf_count, value, offset, size)
            for leaf_count, offset, size, value
            in self.obj
        )

#flat_tree = flat_tree_mix_indices_oo
flat_tree = flat_tree_append_indices

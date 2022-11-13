from . import mix_indices_oo, mix_indices, append_indices

__version__ = '0.0.0'

class flat_tree_append_indices:
    def __init__(self, degree = 2, initial_indices = []):
        for leaf_count, value, offset, size in initial_indices:
            assert offset == 0
        self.obj = append_indices.append_indices(
            degree, [
                (leaf_count, size, value)
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
        sum = 0
        for leaf_count, size, value in self.obj:
            yield (leaf_count, value, sum, size)
            sum += size

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

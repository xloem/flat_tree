# indexes a balanced tree of past indices
# publish paired with every write to retain a lookup
class append_indices(list):
    def __init__(self, degree = 2, initial_indices = []):
        super().__init__(*initial_indices)
        self.degree = degree
        self.leaf_count = sum((leaf_count for leaf_count, value in self))
    def append(self, last_indices_id):
        self.leaf_count += 1
        my_leaf_count = self.leaf_count
        idx = -1
        for idx, (leaf_count, value) in enumerate(self):
            if leaf_count * self.degree <= my_leaf_count:
                break
            my_leaf_count -= leaf_count
        else:
            idx += 1
        self[idx:] = [(my_leaf_count, last_indices_id)]

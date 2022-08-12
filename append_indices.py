# indexes a balanced tree of past indices
# every write, publish a .copy() paired with data, then pass the locator to .append() to index it

class append_indices(list):

    def __init__(self, degree = 2, initial_indices = []):
        super().__init__(*initial_indices)
        self.degree = degree
        self.leaf_count, self.size = 0, 0
        for leaf_count, size, value in self:
            self.leaf_count += leaf_count
            self.size += size

    def append(self, added_size, last_publish):
        self.leaf_count += 1
        self.size += added_size

        new_leaf_count = self.leaf_count
        new_size = self.size

        for idx, (branch_leaf_count, branch_size, branch_id) in enumerate(self):
            if branch_leaf_count * self.degree <= new_leaf_count:
                break
            new_leaf_count -= branch_leaf_count
            new_size -= branch_size
        else:
            idx = len(self)

        self[idx:] = [(new_leaf_count, new_size, last_publish)]

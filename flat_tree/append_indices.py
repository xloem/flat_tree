# indexes a balanced tree of past indices
# every write, publish a .copy() paired with data, then pass the locator to .append() to index it

class append_indices(list):

    def __init__(self, degree = 2, initial_indices = []):
        super().__init__(*initial_indices)
        self.degree = degree
        self.leaf_count, self.size = 0, 0
        for leaf_count, value, offset, size in self:
            assert offset == self.size
            self.leaf_count += leaf_count
            self.size += size

    def append(self, last_publish, added_size, added_data):
        new_leaf_count = self.leaf_count
        new_size = self.size
        new_indices = list(self)

        for idx, (branch_leaf_count, branch_id, branch_offset, branch_size) in enumerate(self):
            if branch_leaf_count * self.degree <= new_leaf_count:
                new_indices[idx:] = (
                    (new_leaf_count, last_publish, branch_offset, new_size),
                )
                break
            new_leaf_count -= branch_leaf_count
            new_size -= branch_size

        new_indices.append(
            (-1, added_data, self.size, added_size)
        )

        total_size = self.size + added_size
        total_leaf_count = self.leaf_count + 1

        assert total_size == sum((size for leaf_count, id, offset, size in new_indices))
        assert total_leaf_count == sum((abs(leaf_count) for leaf_count, id, offset, size in new_indices))
        assert all(
            left_offset + left_size == right_offset
            for (_, _, left_offset, left_size), (_, _, right_offset, right_size)
            in zip(new_indices[:-1], new_indices[1:])
        )

        self[:] = new_indices
        self.size = total_size
        self.leaf_count = total_leaf_count

class append_indices(list):
    def __init__(self, degree = 2, initial_indices = []):
        super().__init__(*initial_indices)
        self.degree = degree
        self.degree = degree
        self.leaf_count, self.size = 0, 0
        for leaf_count, size, value in self:
            self.leaf_count += leaf_count
            self.size += size
        self.splice_queue = []

    def _insert(self, last_publish, *ordered_splices):
        # a reasonable next step is to provide for truncation appends, where a tail of the data is replaced with new data

        # currently only performs 1 append
        assert len(ordered_splices) == 1

        for spliced_out_start, spliced_out_stop, spliced_in_size in ordered_splices:
            #assert spliced_out_start == self.size # truncation appends are drafted but untested
            assert spliced_out_stop == self.size

            self.leaf_count += 1
            self.size += spliced_in_size

            new_leaf_count = self.leaf_count
            new_offset = 0
    
            for idx, (branch_leaf_count, branch_offset, branch_size, branch_id) in enumerate(self):
                if branch_leaf_count * self.degree <= new_leaf_count:
                    break
                new_leaf_count -= branch_leaf_count
                new_offset += branch_size
            else:
                idx = len(self)
    
            self[idx:] = ((new_leaf_count, new_offset, spliced_out_start + spliced_in_size - new_offset, last_publish),)

    def append(self, last_publish, added_size):
        self._insert(last_publish, (self.size, self.size, added_size))

    def snap(self, data):
        return (self.copy(), data)

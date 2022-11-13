class append_indices(list):
    def __init__(self, degree = 2, initial_indices = []):
        super().__init__(initial_indices)
        self.degree = degree
        self.leaf_count, self.size = 0, 0
        for branch_leaf_count, branch_offset, branch_size, branch_id in self:
            self.leaf_count += branch_leaf_count if branch_leaf_count > 0 else 1
            self.size += branch_size

        #self.splice_queue = []

    def _insert(self, last_publish, *ordered_splices):
        # a reasonable next step is to provide for truncation appends, where a tail of the data is replaced with new data

        # currently only performs 1 append
        assert len(ordered_splices) == 1

        for spliced_out_start, spliced_out_stop, spliced_in_size, spliced_in_data in ordered_splices:
            assert spliced_out_start == self.size # until testing truncation appends
            assert spliced_out_stop == self.size

            balanced_size = 0
            balanced_leaf_count = 0
            #leaf_count_of_partial_index_at_end_tmp = 0
            #proposed_leaf_count = self.leaf_count - leaf_count_of_partial_index_at_end_tmp
            #new_node_leaf_count = self.leaf_count # + 1
    
            for idx, (branch_leaf_count, branch_offset, branch_size, branch_id) in enumerate(self):
                if branch_leaf_count * self.degree <= self.leaf_count - balanced_leaf_count: #proposed_leaf_count
                    break
                #if new_node_offset + branch_size > spliced_out_start:
                #    break
                balanced_size += branch_size
                balanced_leaf_count += branch_leaf_count
                #proposed_leaf_count -= branch_leaf_count
                #new_node_leaf_count -= branch_leaf_count
                #new_total_leaf_count += branch_leaf_count
            else:
                idx = len(self)

            assert self.size - balanced_size == sum((size for leaf_count, offset, size, value in self[idx:]))

            self[idx:] = (
                #(leaf_count_of_partial_index_at_end_tmp, balanced_size, spliced_out_start - balanced_size, last_publish),
                (self.leaf_count - balanced_leaf_count, balanced_size, self.size - balanced_size, last_publish),
                (-1, 0, spliced_in_size, spliced_in_data)
            )

            #self.size = spliced_out_start + spliced_in_size
            ##assert spliced_out_start == running_size
            #self.leaf_count = running_leaf_count + leaf_count_of_partial_index_at_end_tmp + 1
            self.size += spliced_in_size
            self.leaf_count += 1

            assert self.size == sum((size for leaf_count, offset, size, value in self))
            assert self.leaf_count == sum((abs(leaf_count) for leaf_count, offset, size, value in self))

    def append(self, last_publish, added_size, added_data):
        self._insert(last_publish, (self.size, self.size, added_size, added_data))

    def snap(self, data):
        return (self.copy(), data)

#class node:
#    def __init__(self, length, data, height=0, leaf_count=1, age=0):
#        self.length = length
#        self.data = data
#        self.height = height
#        self.leaf_count = leaf_count
#        self.age = age
#    def __len__(self):
#        return self.length
#    def is_leaf(self):
#        return self.height == 0
#    def is_full(self, degree = 2):
#        return self.leaf_count == degree ** self.height
#    def region(self, start, end, path = [], height=0, leaf_count=1, relative_to=0):
#        return Region(start, end, self, path, height, leaf_count, relative_to)
#
#class Region(node):
#    def __init__(self, start, end, node, path = [], height=0, leaf_count=1, relative_to=0):
#        super().__init__(end - start, node, height=height, leaf_count=leaf_count, age=node.age)
#        self.offset = start - relative_to
#        self.path = list(path)
#        self.path.append(self.data)
#        self.single_child_descendents = []
#        self.child_count = 0
#        if not chunk.is_leaf() and (leaf_count==1 or height==0):
#            assert leaf_count==1 and height==0
#            # calculate leaf_count and height
#            self.leaf_count = 0
#            self.height = 1
#            for entry in self.flush_entries():
#                self.leaf_count += entry.leaf_count
#                self.height = max(self.height, entry.height + 1)
#                self.child_count += 1
#                if entry.single_child_descendents:
#                    self.single_child_descendents.extend(entry.single_child_descendents)
#                elif entry.child_count == 1:
#                    self.single_child_descendents.append(entry)
#    def flush_entries(self):
#        assert not self.data.is_leaf()
#        start = 0
#        for entry in self.data.data:
#            end = start + len(entry)
#            if start < self.offset + self.length and end > self.offset:
#                yield entry.region(max(start, self.offset), min(end, self.offset + self.length), self,path)
#            start = end
#    def chunk_data(self):
#        assert self.is_leaf()
#        return self.data.data[self.offset : self.offset + self.length]
#    def region(self, *params, **kwparams):
#        return self.data.region(*params, **kwparams)

class data_leaf:
    def __init__(self, locator, length):
        self.locator = locator
        self.length = length

class storage:
    def store(self, data):
        raise NotImplementedError()
    def fetch(self, locator):
        raise NotImplementedError()

class index_node(list):
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

                #self.region(balanced_size, balanced_size + new_size, locator = last_publish),
                (self.leaf_count - balanced_leaf_count, balanced_size, self.size - balanced_size, last_publish),

                
                (-1, 0, spliced_in_size, spliced_in_data)
            )

            #self.size = spliced_out_start + spliced_in_size
            ##assert spliced_out_start == balanced_size
            #self.leaf_count = balanced_leaf_count + leaf_count_of_partial_index_at_end_tmp + 1
            self.size += spliced_in_size
            self.leaf_count += 1

            assert self.size == sum((size for leaf_count, offset, size, value in self))
            assert self.leaf_count == sum((abs(leaf_count) for leaf_count, offset, size, value in self))

    def append(self, last_publish, added_size, added_data):
        self._insert(last_publish, (self.size, self.size, added_size, added_data))

    def snap(self, data):
        return (self.copy(), data)

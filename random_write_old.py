import bisect

class Chunk:
    def __init__(self, start, end, data, height=0, leaf_count=1, age=0):
        self.start = start
        self.end = end
        self.data = data
        self.height = height
        self.leaf_count = leaf_count
        self.age = age
    def __len__(self):
        return self.end - self.start
    def is_leaf(self):
        return self.height == 0
    def is_full(self):
        return self.leaf_count == (1 << self.height)
    def is_power_of_2(self):
        v = self.leaf_count
        return v & (v - 1) == 0

    def region(self, start, end, path = [], height=0, leaf_count=1):
        return Region(start, end, self, path, height, leaf_count)

class Region(Chunk):
    def __init__(self, start, end, chunk, path = [], height=0, leaf_count=1):
        super().__init__(start, end, chunk, height=height, leaf_count=leaf_count, age=chunk.age)
        self.path = list(path)
        self.path.append(self.data)
        self.single_child_descendents = []
        self.child_count = 0
        if not chunk.is_leaf() and (leaf_count==1 or height==0):
            assert leaf_count==1 and height==0
            # calculate leaf_count and height
            self.leaf_count = 0
            self.height = 1
            for entry in self.flush_entries():
                self.leaf_count += entry.leaf_count
                self.height = max(self.height, entry.height + 1)
                self.child_count += 1
                if entry.single_child_descendents:
                    self.single_child_descendents.extend(entry.single_child_descendents)
                elif entry.child_count == 1:
                    self.single_child_descendents.append(entry)
    def flush_entries(self):
        assert not self.data.is_leaf()
        return (
            entry.region(max(entry.start, self.start), min(entry.end, self.end), self.path)
            for entry in self.data.data
            if entry.start < self.end and entry.end > self.start
        )
    def chunk_data(self):
        assert self.is_leaf()
        return self.data.data[self.start - self.data.start : self.end - self.data.start]
    def region(self, *params, **kwparams):
        return self.data.region(*params, **kwparams)

class FlushRegion:
    def __init__(self, *entries, left_write = None, right_write = None):
        for left, right in zip(entries[:-1], entries[1:]):
            assert left.end <= right.start
        if left_write is not None and len(entries):
            assert left_write.end <= right_write.start
            if right_write is not None:
                assert left_write.end <= right_write.start
        if right_write is not None and len(entries):
            assert right_write.start >= entries[-1].end
        self.entries = entries
        self.left_write = left_write
        self.right_write = right_write

class Flush(Chunk):
    def __init__(self, prev_flush = None):
        if prev_flush is not None:
            super().__init__(prev_flush.start, prev_flush.end, [], height=1, leaf_count=0, age=prev_flush.age+1)
            self.max_height = prev_flush.leaf_count.bit_length()
            prev_entry = prev_flush.region(prev_flush.start, prev_flush.end)
            self.add(prev_entry)
        else:
            super().__init__(None, None, [], height=1, leaf_count=0)
            self.max_height = 1
    def add(self, *adjacents):
        adjacents = list(adjacents)
        if self.start is None:
            self.start = adjacents[0].start
            self.end = adjacents[-1].end
        else:
            self.start = min(self.start, adjacents[0].start)
            self.end = max(self.end, adjacents[-1].end)


        # expand adjacents that are too deep [should go after start_idx and end_idx are adjust, to find correct max_height easier]
        idx = 0
                # could update this algorithm to: accumulate things that aren't leaves
                # after a run, calculate their shared max_height
                # then shallow them all to that minus one, and we're the new root
                # seems like the big update of interest
                    # change: now bringing up descendents without siblings
        while idx < len(adjacents):
            entry = adjacents[idx]
            if entry.single_child_descendents:
                print(f'merging {len(entry.single_child_descendents)} single children')
                subadjacents = []
                shallow_start = entry.start
                for descendent in entry.single_child_descendents:
                    if shallow_start != descendent.start:
                        subadjacents.append(entry.region(shallow_start, descendent.start))
                    subadjacents.append(descendent)
                    shallow_start = descendent.end
                if shallow_start != entry.end:
                    subadjacents.append(entry.region(shallow_start, entry.end))
                adjacents[idx:idx+1] = subadjacents
            #elif entry.height + 1 > self.max_height:
            #    print(f'expanding a branch with depth {entry.height+1}')
            #    subadjacents = []
            #    shallow_start = entry.start
            #    shallow_end = shallow_start
            #    for subentry in entry.flush_entries():
            #        if subentry.height + 2 > self.max_height:
            #            if shallow_end != shallow_start:
            #                subadjacents.append(entry.region(shallow_start, shallow_end))
            #            subadjacents.append(subentry)
            #            shallow_start = subentry.end
            #        shallow_end = subentry.end
            #    if shallow_end != shallow_start:
            #        subadjacents.append(entry.region(shallow_start, shallow_end))
            #    adjacents[idx:idx+1] = subadjacents
            else:
                idx += 1

        # first idx with end >= start
        start_idx = bisect.bisect_left([entry.end for entry in self.data], adjacents[0].start)
        # first idx with start > end
        end_idx = bisect.bisect_right([entry.start for entry in self.data], adjacents[-1].end, start_idx)
        replaced = self.data[start_idx:end_idx]
        if len(replaced):
            if replaced[0].start < adjacents[0].start:
                adjacents.insert(
                    0,
                    replaced[0].region(replaced[0].start, adjacents[0].start)
                )
                if start_idx > 0 and replaced[0].end > adjacents[1].start:
                    # the trimmed entry may have fewer leaves and itself merge with its neighbor
                    start_idx -= 1
                    replaced.insert(0, self.data[start_idx])
                    adjacents.insert(0, self.data[start_idx])
            if replaced[-1].end > adjacents[-1].end:
                adjacents.append(
                    replaced[-1].region(adjacents[-1].end, replaced[-1].end)
                )
                if end_idx < len(self.data) and replaced[-1].start < adjacents[-2].end:
                    # the trimmed entry may have fewer leaves and itself merge with its neighbor
                    replaced.append(self.data[end_idx])
                    adjacents.append(self.data[end_idx])
                    end_idx += 1

        for idx, entry in reversed(list(enumerate(adjacents))):
            if entry.leaf_count == 0:
                # no leaves left in this branch, remove
                adjacents.pop(idx)
                continue
            count = 0
            subentry = entry
            while count <= 1 and not subentry.data.is_leaf():
                # make branches shallower by splicing out roots with only one child
                parent_entry = subentry
                count = 0
                for subentry in parent_entry.flush_entries():
                    count += 1
                    if count > 1:
                        subentry = parent_entry
                        break
            if subentry is not entry:
                # some internodes were removed
                adjacents[idx] = subentry

        idx = len(adjacents) - 1
        while idx > 0:
            idx -= 1
            left_adjacent = adjacents[idx]
            right_adjacent = adjacents[idx+1]

            # merge writes
            if (
                left_adjacent.age == self.age and
                right_adjacent.age == self.age and
                left_adjacent.end == right_adjacent.start
            ):
                left_adjacent.data = Chunk(
                    left_adjacent.start,
                    right_adjacent.end,
                    left_adjacent.chunk_data() + right_adjacent.chunk_data(),
                    age = self.age
                )
                left_adjacent.end = right_adjacent.end
                adjacents.pop(idx+1)
                continue

            # merge branches with shared parents
            shared_path = [
                left_parent for left_parent, right_parent
                in zip(left_adjacent.path, right_adjacent.path)
                if left_parent is right_parent
            ]
            if len(shared_path) > 0 and left_adjacent.height + len(left_adjacent.path) - len(shared_path) < self.max_height and right_adjacent.height + len(right_adjacent.path) - len(shared_path) < self.max_height:
                if left_adjacent.end != right_adjacent.start:
                    assert left_adjacent.end < right_adjacent.start
                    between_entry = shared_path[-1].region(left_adjacent.end, right_adjacent.start)
                    if between_entry.leaf_count > 0:
                        # the shared root contains leaves in between that have been removed
                        continue
                print(f'Merging {len(left_adjacent.path)}:{left_adjacent.height}, {len(right_adjacent.path)}:{right_adjacent.height} -> {len(shared_path)}:{left_adjacent.height + len(left_adjacent.path) - len(shared_path)}')
                merged = shared_path[-1].region(
                    left_adjacent.start,
                    right_adjacent.end,
                    path = shared_path,
                    # letting Region recalculate these is a quick way to handle overlap
                    #leaf_count = left_adjacent.leaf_count + right_adjacent.leaf_count,
                    #height = left_adjacent.height + len(left_adjacent.path) - len(shared_path)
                )
                #assert merged.leaf_count == merged.data.check_leaf_count(merged.start, merged.end)
                adjacents[idx:idx+2] = [merged]

        # ensure all leaves are balanced trees with appropriate height
        idx = 0
        while idx < len(adjacents):
            entry = adjacents[idx]
            if entry.height >= self.max_height or not entry.is_full():
                adjacents[idx:idx+1] = entry.flush_entries()
            #elif not entry.is_full():
            #    subadjacents = []
            #    last_idx = idx
            #    last_end = entry.start
            #    count = 0
            #    for next_idx, subentry in enumerate(entry.flush_entries()):
            #        subadjacents.append(subentry)
            #        next_count = count + subentry.leaf_count
            #        if is_2_power(next_count):
            #            subadjacents.append(
#
#                # - each entry is made of full entries
#                # - so we want as many entries together as are still full
#                    # why is it not doing that already
#                    # once it is a power of 2 large, it should be treated as full
            else:
                idx += 1


        self.data[start_idx:end_idx] = adjacents
        # using Region to recalculate leaf_count is a quick-to-implement way to handle not double-counting chunks that span trimmed groups
        proxy_entry = self.region(self.data[0].start, self.data[-1].end)
        self.leaf_count = proxy_entry.leaf_count
        self.height = proxy_entry.height
        #self.height = max((entry.height for entry in self.data)) + 1
        #self.check_leaf_count(self.start, self.end)

        assert self.leaf_count > 0

        self.max_height = self.leaf_count.bit_length()

        #assert self.max_height >= self.height # oops this isn't met yet due to dependency order above, calculations used last value

    def write(self, offset, data):
        chunk = Chunk(offset, offset + len(data), data, age=self.age)
        entry = chunk.region(offset, offset + len(data))
        return self.add(entry)
    def read(self, start, max_end = float('inf')):
        # first idx with end > start
        idx = bisect.bisect_right([entry.end for entry in self.data], start)
        if idx == len(self.data):
            return bytes(4096)
        entry = self.data[idx]
        if entry.start > start:
            end = min(max_end, entry.start)
            return bytes(end - start)
        end = min(max_end, entry.end)
        if entry.data.is_leaf():
            datastart = start - entry.data.start
            dataend = end - entry.data.start
            return entry.data.data[datastart : dataend]
        else:
            return entry.data.read(start, end)
    def check_leaf_count(self, start, end):
        leaf_count = 0
        height = 1
        wrapper = self.region(start, end)
        for entry in wrapper.flush_entries():
            if type(entry.data) is Flush:
                entry_leaf_count = entry.data.check_leaf_count(entry.start, entry.end)
                assert entry_leaf_count == entry.leaf_count
                leaf_count += entry_leaf_count
            else:
                leaf_count += entry.data.leaf_count
            height = max(height, entry.height + 1)
        assert leaf_count == wrapper.leaf_count
        assert height == wrapper.height
        if start == self.start and end == self.end:
            assert leaf_count == self.leaf_count
            assert height == self.height # oops not met yet
        return leaf_count



def main():
    import random
    random.seed(0)
    SIZE=4096
    comparison = bytearray(SIZE)
    #import mmap
    #comparison = mmap.mmap(-1, SIZE)
    store = Flush()
    def compare(store, comparison):
        offset = 0
        while offset < len(comparison):
            data = store.read(offset)[:len(comparison) - offset]
            assert data == comparison[offset:offset+len(data)]
            offset += len(data)
        store.check_leaf_count(store.start, store.end)
        return True
    for flushes in range(1024):
        for writes in range(random.randint(1,16)):
            start = random.randint(0, SIZE-1)
            size = min(SIZE-start, random.randint(1, 1024))
            #size = min(SIZE-start, random.randint(1, 128))
            #start = len(comparison)
            #size = random.randint(1,128)
            end = start + size
            data = random.getrandbits(size*8).to_bytes(size, 'little')
            store.write(start, data)
            comparison[start:end] = data
            #compare(store, comparison)
            #print('OK', len(store.data), 'x', store.height, '/', store.max_height, 'count =', store.leaf_count, 'flushes =', flushes, 'writes =', writes)#, offset)
        compare(store, comparison)
        print('OK', len(store.data), 'x', store.height, '/', store.max_height, '; count =', store.leaf_count, '; flushes =', flushes, '; full =', store.is_full())#, writes)#, offset)
        store = Flush(prev_flush = store)
        compare(store, comparison)

if __name__ == '__main__':
    main()
    #import cProfile
    #cProfile.run('main()')

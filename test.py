from append_indices_tree import append_indices

index = append_indices()
stored_indices = {}

import random
data = [random.random() for x in range(16)]
for offset, new_data in enumerate(data):
    last_id = index.leaf_count
    stored_indices[last_id] = ([*index], offset + 1, new_data)
    index.append(last_id)

def iterate(index, start_offset, end_offset):
    for subleafcount, subid in index:
        subindex, subendoffset, subdata = stored_indices[subid]
        if subendoffset > start_offset:
            yield from iterate(subindex, start_offset, end_offset)
            if subendoffset > end_offset:
                return
            yield subdata
            start_offset = subendoffset

assert data == [*iterate(index, 0, offset + 1)]


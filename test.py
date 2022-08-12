from append_indices_tree import append_indices

index = append_indices(degree=3)
stored_indices = {}

import random
data = [random.random() for x in range(24)]
for offset, new_data in enumerate(data):
    id = index.leaf_count
    stored_indices[id] = (index.copy(), new_data)
    index.append(id, 1)

def iterate(index, start_offset, end_offset):
    subendoffset = 0
    for subleafcount, subsize, subid in index:
        subindex, subdata = stored_indices[subid]
        subendoffset += subsize
        if subendoffset > start_offset:
            yield from iterate(subindex, start_offset, end_offset)
            if subendoffset > end_offset:
                return
            yield subdata
            start_offset = subendoffset

print(data)
cmp = [*iterate(index, 0, index.size)]
print(cmp)

assert data == cmp

print(index)

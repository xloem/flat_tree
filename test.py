from mix_indices import append_indices

index = append_indices(degree=3)
stored_indices = {}

import random
data = [random.randbytes(random.randint(1,8)) for x in range(24)]

for chunk in data:
    id = index.leaf_count
    stored_indices[id] = (index.copy(), chunk)
    index.append(id, len(chunk))

def iterate(index, start_offset, end_offset):
    subendoffset = 0
    for subleafcount, suboffset, subsize, subid in index:
        subindex, subdata = stored_indices[subid]
        subendoffset += subsize
        if subendoffset > start_offset:
            data = b''.join(iterate(subindex, start_offset, end_offset))
            yield data
            if subendoffset > end_offset:
                return
            yield subdata
            start_offset = subendoffset

data = b''.join(data)
print(data)
cmp = b''.join(iterate(index, 0, index.size))
print(cmp)

assert data == cmp

print(index)

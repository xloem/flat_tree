import append_indices
#import mix_indices

index = append_indices.append_indices(degree=3)
stored_indices = {}

import random
data = [random.randbytes(random.randint(1,8)) for x in range(24)]

for chunk in data:
    id = index.leaf_count
    stored_indices[id] = index.copy()
    index.append(id, len(chunk), chunk)

def iterate(index, start_offset, end_offset):
    subendoffset = 0
    for subleafcount, *_, subsize, subid in index:
        substartoffset = subendoffset
        subendoffset += subsize
        if subendoffset > start_offset:
            if subleafcount == -1:
                data = subid
            else:
                subindex = stored_indices[subid]
                #adjusted_start = start_offset - substartoffset + suboffset
                #adjusted_end = end_offset - substartoffset + suboffset
                #data = b''.join(iterate(subindex, adjusted_start, min(adjusted_end, subsize - adjusted_start)))
                data = b''.join(iterate(subindex, start_offset, end_offset))
            yield data
            if subendoffset > end_offset:
                return
            start_offset = subendoffset

data = b''.join(data)
print(data)
cmp = b''.join(iterate(index, 0, index.size))
print(cmp)

assert data == cmp

print(index)

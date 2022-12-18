#import append_indices
#import mix_indices as append_indices
from flat_tree import flat_tree#_mix_indices_oo as flat_tree
from flat_tree.store import ListStore

index = flat_tree(degree=3)
#stored_indices = {}
stored_indices = ListStore()

import random
random.seed(0)
data = [random.randbytes(random.randint(1,8)) for x in range(24)]

for chunk in data:
    #id = index.leaf_count
    #stored_indices[id] = index.snap()
    id = stored_indices.store_index(index.snap())
    #chunkid = stored_indices.store(chunk)
    index.append(id, len(chunk), chunk)

def iterate(index, start_offset, end_offset):
    subendoffset = 0
    for subleafcount, subid, suboffset, subsize in index:
        substartoffset = subendoffset
        subendoffset += subsize
        if subendoffset > start_offset:
            if subleafcount == -1:
                data = subid
                yield data
            else:
                subindex = stored_indices.fetch(subid)
                adjusted_start = start_offset - substartoffset + suboffset
                adjusted_end = end_offset - substartoffset + suboffset
                #data = b''.join(iterate(subindex, adjusted_start, min(adjusted_end, subsize - adjusted_start)))
                data = list(iterate(subindex, adjusted_start, min(adjusted_end, subsize + suboffset)))
                #data = b''.join(iterate(subindex, start_offset, end_offset))
                #data = list(iterate(subindex, start_offset, end_offset))
                assert len(data) == subleafcount
                yield from data
            if subendoffset > end_offset:
                return
            start_offset = subendoffset

data = b''.join(data)
print(data)
print(index)
cmp = b''.join(iterate(index, 0, index.byte_count))
print(cmp)

assert data == cmp

#print(index)

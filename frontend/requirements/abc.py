#!/usr/bin/python
import itertools

res = []
res[:] = 'abc'
res2 = [[i] for i in 'abc']

a = [sub1 + sub2 for sub1 in res for sub2 in reversed(res) if sub1 != sub2]

print(
    list(
        itertools.permutations('ABCD', 4)
    )
)

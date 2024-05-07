#!/usr/bin/env python3

import sys

limit = int(sys.argv[1])

completed = set()
for line in open("custom_stats.csv", 'r'):
    if line.startswith("accession,"):
        continue
    else:
        acc = line.rstrip().split(",")[0]
        completed.add(acc)

o = open("genomes.csv", 'w')
count = 0
for line in open("local_manifest.txt", 'r'):
    if line.startswith("total"):
        continue
    vals = line.rstrip().split()
    prefix = vals[-1].replace(".fna.gz", "")
    if prefix not in completed:
        o.write(prefix + "\n")
        count += 1
        if count == limit:
            break
o.close()

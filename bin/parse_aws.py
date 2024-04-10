#!/usr/bin/env python3

import sys

limit = int(sys.argv[1])

completed = set()
for line in open("genome_stats.csv", 'r'):
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
    this_acc = vals[-1].replace(".fna.gz", "")
    if this_acc not in completed:
        o.write(this_acc + "\n")
        count += 1
        if count == limit:
            break
o.close()

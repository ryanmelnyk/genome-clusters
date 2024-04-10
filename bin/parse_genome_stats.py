#!/usr/bin/env python3

import sys

limit = int(sys.argv[1])

passing = set()
for line in open("genome_stats.csv", 'r'):
    if line.startswith("accession,"):
        continue
    else:
        vals = line.rstrip().split(",")
        # check n50
        if int(vals[2]) < 20000:
            continue
        # check % single - both completeness and contam
        elif float(vals[4]) < 90.0:
            continue
        else:
            passing.add(vals[0])

clustered = set()
for line in open("clusters.csv", 'r'):
    if line.startswith("accession,"):
        continue
    else:
        vals = line.rstrip().split(",")
        clustered.add(vals[0])

o = open("genomes.csv", 'w')
count = 0
for line in open("aws_manifest.txt", 'r'):
    if line.startswith("total"):
        continue
    vals = line.rstrip().split()
    this_acc = vals[-1].replace(".fna.gz", "")
    if this_acc in passing and this_acc not in clustered:
        o.write(vals[-1] + "\n")
        count += 1
        if count == limit:
            break
o.close()

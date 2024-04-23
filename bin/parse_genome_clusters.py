#!/usr/bin/env python3

import sys
from Bio import SeqIO

limit = int(sys.argv[1])

centroids = set()
for line in open("clusters.csv", 'r'):
    if line.startswith("accession,"):
        continue
    else:
        vals = line.rstrip().split(",")
        if vals[1] == "True":
            centroids.add(vals[0])

classified = set()
for line in open("gtdbtk_taxonomy.tsv", 'r'):
    if line.startswith("user_genome\t"):
        continue
    else:
        vals = line.rstrip().split("\t")
        classified.add(vals[0].replace(".fna", ""))

o = open("genomes.csv", 'w')
count = 0
for line in open("aws_manifest.txt", 'r'):
    if line.startswith("total"):
        continue
    vals = line.rstrip().split()
    this_acc = vals[-1].replace(".fna.gz", "")
    if this_acc in centroids and this_acc not in classified:
        o.write(vals[-1] + "\n")
        count += 1
        if count == limit:
            break
o.close()

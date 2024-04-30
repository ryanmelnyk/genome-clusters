#!/usr/bin/env python3

import sys
from Bio import SeqIO

limit = int(sys.argv[1])

msa = set()
for seq in SeqIO.parse(open("gtdbtk_msa.faa", 'r'), 'fasta'):
    msa.add(seq.id.replace(".fna", ""))

genomes = set()
for line in open("clusters.csv", 'r'):
    if line.startswith("accession,"):
        continue
    else:
        vals = line.rstrip().split(",")
        genomes.add(vals[0])

o = open("genomes.csv", 'w')
count = 0
for line in open("aws_manifest.txt", 'r'):
    if line.startswith("total"):
        continue
    vals = line.rstrip().split()
    this_acc = vals[-1].replace(".fna.gz", "")
    if this_acc in genomes and this_acc not in msa:
        o.write(vals[-1] + "\n")
        count += 1
        if count == limit:
            break
o.close()

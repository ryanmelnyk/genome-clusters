#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov

from Bio import SeqIO
import sys

seqlens = {}

for seq in SeqIO.parse(open(sys.argv[1], 'r'), 'fasta'):
    seqlens[seq.id] = len(seq)

o = open("input.abc", 'w')
for line in open(sys.argv[2], "r"):
    vals = line.rstrip().split("\t")
    if vals[0] == vals[1]:
        continue
    elif float(vals[3]) > (0.9 * seqlens[vals[0]]):
        o.write("\t".join([vals[i] for i in [0,1,11]]) + "\n")
o.close()
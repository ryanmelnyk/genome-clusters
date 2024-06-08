#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov


from Bio import SeqIO
import os
import sys

o = open("combined.faa", 'w')

for line in open(sys.argv[1], 'r'):
    acc = line.rstrip()
    for seq in SeqIO.parse(open(f"{acc}.faa", 'r'), 'fasta'):
        seq.id  = f"{seq.id}|{acc}"
        SeqIO.write(seq, o, 'fasta')
o.close()


    
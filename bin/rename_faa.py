#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov


from Bio import SeqIO
import os

o = open("combined.faa", 'w')

for f in os.listdir("."):
    if f == "combined.faa":
        continue
    
    if f.endswith(".faa"):
        acc = f.replace(".faa", "")
        for seq in SeqIO.parse(open(f, 'r'), 'fasta'):
            seq.id  = f"{seq.id}|{acc}"
            SeqIO.write(seq, o, 'fasta')
o.close()        


    
#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov


from Bio import SeqIO
import sys
from collections import Counter


# parse the locus tags file

locus = {}
print("Parsing tags...")
for line in open(sys.argv[1], 'r'):
    vals = line.rstrip().split("\t")
    if vals[0] == "group_id":
        header = vals[1:]
    else:
        vals = line.rstrip().split("\t")
        tags = [v.split(",") for v in vals[1:]]
        locus[vals[0]] = dict(zip(header, tags))
        

# parse the fasta file
print("Parsing fasta...")
fasta = { h: {} for h in header }
desc = { h: {} for h in header } 

for seq in SeqIO.parse(open("combined.faa", 'r'), 'fasta'):
    vals = seq.id.split("|")
    fasta[vals[1]][vals[0]] = str(seq.seq)
    desc[vals[1]][vals[0]] = " ".join(seq.description.split(" ")[2:])

for group in locus:
    print(f"\t{group}")
    o = open(f"group_fasta/{group}.faa", 'w')
    for strain in locus[group]:
        for gene in locus[group][strain]:
            if gene != "None":
                description = desc[strain][gene]
                seqdata = fasta[strain][gene]
                o.write(f">{gene}|{strain} {description}\n")
                o.write(f"{seqdata}\n")
    o.close()
    
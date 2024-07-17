#!/usr/bin/env python3

import sys
from Bio import SeqIO

dir = "/usr2/people/melnyk/genomedb/metadata"
accessions = set([line.rstrip() for line in open(sys.argv[1], 'r')])

o = open(sys.argv[2], 'w')
for seq in SeqIO.parse(open(f"{dir}/gtdbtk_msa.faa", 'r'), 'fasta'):
    acc_id = seq.id.replace(".fna", "")
    if acc_id in accessions:
        seq.id = acc_id
        SeqIO.write(seq, o, 'fasta')
o.close()

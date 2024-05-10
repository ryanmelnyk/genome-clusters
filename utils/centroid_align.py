#!/usr/bin/env python3


from Bio import SeqIO

dir = "/usr2/people/melnyk/genomedb/metadata"

centroids = set()
for line in open(f"{dir}/clusters.csv", 'r'):
    vals = line.rstrip().split(",")
    if vals[1] == "True":
        centroids.add(vals[0])

o = open("tmp/centroid_msa.faa", 'w')
for seq in SeqIO.parse(open(f"{dir}/gtdbtk_msa.faa", 'r'), 'fasta'):
    acc_id = seq.id.replace(".fna", "")
    if acc_id in centroids:
        seq.id = acc_id
        SeqIO.write(seq, o, 'fasta')
o.close()

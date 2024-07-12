#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov

import re
import sys
import os
from collections import defaultdict

mm_clusters = {}

print("Reading mmseqs clusters...")
mm_count = 0
for line in open(sys.argv[2]):
    vals = line.rstrip().split("\t")
    if vals[0] == vals[1]:
        continue
    else:
        if vals[0] not in mm_clusters:
            mm_clusters[vals[0]] = set()
            mm_count += 1
            if mm_count % 100000 == 0:
                print(f"\t{int(mm_count/100000)}00K mmseqs clusters parsed...")
        mm_clusters[vals[0]].add(vals[1])

genomes = [line.rstrip() for line in open("genomes.txt", 'r')]
genome_string = "\t".join(genomes)

tag = sys.argv[1].split(".")[1]
o = open(f"locustags.{tag}.csv", 'w')
o.write(f"group_id\t{genome_string}\n")

p = open(f"counts.{tag}.csv", 'w')
p.write(f"group_id\t{genome_string}\n")

print("Parsing mcl clusters...")
mm_found = set()
cluster = 1

for line in open(sys.argv[1], 'r'):
    cluster_id = f"group_{cluster:06d}"
    this_cluster = defaultdict(list)
    for x in line.rstrip().split("\t"):
        vals = x.split("|")
        this_cluster[vals[1]].append(vals[0])
        if x in mm_clusters:
            mm_found.add(x)
            for y in mm_clusters[x]:
                vals = y.split("|")
                this_cluster[vals[1]].append(vals[0])
    tags = []
    counts = []
    gene_count = 0
    for g in genomes:
        if len(this_cluster[g]) == 0:
            tags.append("None")
            counts.append("0")
        else:
            tags.append(",".join(this_cluster[g]))
            counts.append(str(len(this_cluster[g])))
            gene_count += len(this_cluster[g])
    tagstring = "\t".join(tags)
    countstring = "\t".join([str(x) for x in counts])
    o.write(f"{cluster_id}\t{tagstring}\n")
    p.write(f"{cluster_id}\t{countstring}\n")
    print(f"\t{cluster_id}: {str(gene_count)} genes...")
    cluster += 1

print(f"\n{cluster} total clusters in MCL data!")

# dump mmseqs clusters as a group if no members showed up in mcl output
print("Finding any mmseqs clusters not in mcl data...")
for mm in mm_clusters:
    if mm not in mm_found:
        cluster_id = f"group_{cluster:07d}"
        this_cluster = defaultdict(list)
        this_cluster[mm.split("|")[1]].append(mm.split("|")[0])
        for x in mm_clusters[mm]:
            vals = x.split("|")
            this_cluster[vals[1]].append(vals[0])
        gene_count = 0
        tags = []
        counts = []
        for g in genomes:
            if len(this_cluster[g]) == 0:
                tags.append("None")
                counts.append("0")
            else:
                tags.append(",".join(this_cluster[g]))
                counts.append(str(len(this_cluster[g])))
                gene_count += len(this_cluster[g])
        tagstring = "\t".join(tags)
        countstring = "\t".join([str(x) for x in counts])
        o.write(f"{cluster_id}\t{tagstring}\n")
        p.write(f"{cluster_id}\t{countstring}\n")
        print(f"\t{cluster_id}: {str(gene_count)} genes...")
        cluster += 1
        
print(f"\n{cluster} total clusters written to file!\n")
o.close()
p.close()


            
#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov

import re
import sys

mm_clusters = {}

for line in open("mmseqs95_cluster.tsv"):
    vals = line.rstrip().split("\t")
    if vals[0] == vals[1]:
        continue
    else:
        if vals[0] in mm_clusters:
            mm_clusters[vals[0]].append(vals[1])
        else:
            mm_clusters[vals[0]] = [vals[1]]

genomes = [line.rstrip() for line in open("genomes.txt", 'r')]
genome_string = "\t".join(genomes)

tag = sys.argv[1].split(".")[1]
o = open(f"locustags.{tag}.csv", 'w')
o.write(f"group_id\t{genome_string}\n")

p = open(f"counts.{tag}.csv", 'w')
p.write(f"group_id\t{genome_string}\n")

mm_found = set()
cluster = 1
for line in open(sys.argv[1], 'r'):
    this_cluster = {g: [] for g in genomes}
    cluster_id = f"group_{cluster:06d}"
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
    for g in genomes:
        if len(this_cluster[g]) == 0:
            tags.append("None")
            counts.append(0)
        else:
            tags.append(",".join(this_cluster[g]))
            counts.append(len(this_cluster[g]))
    tagstring = "\t".join(tags)
    countstring = "\t".join([str(x) for x in counts])
    o.write(f"{cluster_id}\t{tagstring}\n")
    p.write(f"{cluster_id}\t{countstring}\n")
    cluster += 1
# dump mmseqs clusters as a group if they didn't show up in mcl output 
for mm in mm_clusters:
    if mm not in mm_found:
        this_cluster = {g: [] for g in genomes}
        cluster_id = f"group_{cluster:06d}"
        this_cluster[mm.split("|")[1]].append(mm.split("|")[0])
        for x in mm_clusters[mm]:
            vals = x.split("|")
            this_cluster[vals[1]].append(vals[0])
        tags = []
        counts = []
        for g in genomes:
            if len(this_cluster[g]) == 0:
                tags.append("None")
                counts.append(0)
            else:
                tags.append(",".join(this_cluster[g]))
                counts.append(len(this_cluster[g]))
        tagstring = "\t".join(tags)
        countstring = "\t".join([str(x) for x in counts])
        o.write(f"{cluster_id}\t{tagstring}\n")
        p.write(f"{cluster_id}\t{countstring}\n")
        cluster += 1
        
o.close()
p.close()


            
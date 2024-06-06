#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov

import re
import sys

cd_clusters = {}

cluster = "NA"
centroid = "NA"
others = []

gene_re = ", >(.*)\.\.\. "

for line in open("clustered.faa.clstr"):
    if line.startswith(">"):
        vals = line.rstrip().split()
        if cluster != "NA":
            cd_clusters[centroid] = others
        cluster = int(vals[-1])
        centroid = "NA"
        others = []
    else:
        gene = re.search(gene_re, line.rstrip()).group(1)
        if line.rstrip().endswith("*"):
            centroid = gene
        else:
            others.append(gene)

genomes = [line.rstrip() for line in open("genomes.txt", 'r')]
genome_string = "\t".join(genomes)

tag = sys.argv[1].split(".")[1]
o = open(f"locustags.{tag}.csv", 'w')
o.write(f"group_id\t{genome_string}\n")

p = open(f"counts.{tag}.csv", 'w')
p.write(f"group_id\t{genome_string}\n")

cluster = 1
for line in open(sys.argv[1], 'r'):
    this_cluster = {g: [] for g in genomes}
    cluster_id = f"group_{cluster:06d}"
    for x in line.rstrip().split("\t"):
        vals = x.split("|")
        this_cluster[vals[1]].append(vals[0])
        for y in cd_clusters[x]:
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
o.close()
p.close()


            
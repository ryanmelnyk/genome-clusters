#!/usr/bin/env python3

import sys
from collections import defaultdict

tree = open(sys.argv[1]).read()
dir = "/usr2/people/melnyk/genomedb/metadata"

tax = {}
for line in open(f'{dir}/gtdbtk_taxonomy.tsv', 'r'):
    if line.startswith("user_genome"):
        continue
    else:
        vals = line.rstrip().split("\t")
        tax[vals[0].replace(".fna", "")] = vals[1]

clusters = {}
for line in open(f'{dir}/clusters.csv', 'r'):
    if line.startswith("accession"):
        continue
    vals = line.rstrip().split(",")
    clusters[vals[0]] = vals[2]

for acc_id in clusters:
    name = (
        acc_id + "_" + 
        tax[clusters[acc_id]]
            .split(";")[-1]
            .split("__")[1]
            .replace("_", "")
            .replace(" ", "_")
    )
    tree = tree.replace(acc_id, name)

o = open(sys.argv[2], 'w')
o.write(tree)
o.close()

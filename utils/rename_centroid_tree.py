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

clusters = defaultdict(int)
for line in open(f'{dir}/clusters.csv', 'r'):
    vals = line.rstrip().split(",")
    clusters[vals[2]] += 1

for acc_id in tax:
    try:
        name = acc_id + "_" + "_".join(
            [
                x.split("__")[1].replace("_", "").replace(" ", "_") for x
                in tax[acc_id].split(";")[1:] if x.split("__")[0] != "g"
            ]
        )
    except:
        name = acc_id + f"_{tax[acc_id]}"
    name += f"_{clusters[acc_id]}genomes"
    tree = tree.replace(acc_id, name)

o = open(sys.argv[2], 'w')
o.write(tree)
o.close()

#!/usr/bin/env python3

import os
matched = {}

# pull out already defined centroids from database
for line in open("old_clusters.csv", 'r'):
    if line.startswith("accession,"):
        continue
    else:
        vals = line.rstrip().split(",")
        if vals[1] == "True":
            matched[vals[0]] = "centroid"

# check out mash dist of all new strains vs themselves and old centroids
for line in open("new_dist.txt", 'r'):
    vals = line.rstrip().split()
    ref_acc = vals[0].replace(".fna", "")
    query_acc = vals[1].replace(".fna", "")
    # skip if query against self
    if ref_acc == query_acc:
        continue
    # skip if query acc already defined
    elif query_acc in matched:
        continue
    else:
        # if neither query or ref matched, create new centroid from ref
        if ref_acc not in matched:
            matched[ref_acc] = "centroid"
            matched[query_acc] = ref_acc
        # if the reference is a centroid add query to that cluster
        elif matched[ref_acc] == "centroid":
            matched[query_acc] = ref_acc
        else:
            # ignore the match if it is against a non-centroid
            pass


centroids = set()
o = open("new_clusters.csv", 'w')
# iterate through all genomes in this batch and write centroid info to CSV
for line in open("genomes.csv", 'r'):
    acc = line.rstrip().replace(".fna.gz", "")
    if acc in matched:
        if matched[acc] == "centroid":
            o.write(f"{acc},True,{acc}\n")
            centroids.add(acc)
        else:
            o.write(f"{acc},False,{matched[acc]}\n")
    else:
        # if a genome isn't in the mash dist output at all, it's a centroid
        o.write(f"{acc},True,{acc}\n")
        centroids.add(acc)
o.close()

o = open("new_centroid_list.txt", 'w')
for file in os.listdir("."):
    if file.endswith(".fna"):
        acc = file.replace(".fna", "")
        if acc in centroids:
            o.write(f"{file}\n")
o.close()

o = open("combined_clusters.csv", 'w')
o.write("accession,centroid,centroid_name\n")
for line in open("old_clusters.csv", 'r'):
    if line.startswith("accession,"):
        continue
    else:
        o.write(line)
for line in open("new_clusters.csv", 'r'):
    o.write(line)
o.close()

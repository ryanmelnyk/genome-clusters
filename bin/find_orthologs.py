#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov

import sys
from collections import Counter


# parse the locus tags file

threshold = 0.95

orthos = []
o = open("ortholog_groups.txt", 'w')
for line in open("counts.csv", 'r'):
    if line.startswith("group_id"):
        continue
    else:
        vals = line.rstrip().split("\t")
        if float(vals[1:].count("1"))/float(len(vals[1:])) > threshold:
            o.write(f"{vals[0]}\n")
o.close()
#!/usr/bin/env python3

import os

files = [
    x for x in os.listdir(".") if x.endswith(".csv")
]

o = open("genome_stats.csv", 'w')
header = False
for f in files:
    for line in open(f, 'r'):
        if line.startswith("accession,"):
            if header:
                continue
            else:
                o.write(line)
                header = True
        else:
            o.write(line)

o.close()

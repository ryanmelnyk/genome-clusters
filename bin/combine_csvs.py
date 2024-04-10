#!/usr/bin/env python3

import os

dfs = []

o = open("genome_stats.csv", 'w')

header = False
for f in os.listdir("."):
    if f.endswith(".csv"):
        for line in open(f, 'r'):
            if line.startswith("accession,"):
                if header:
                    continue
                else:
                    o.write(line)
                    header=True
            else:
                o.write(line)

o.close()

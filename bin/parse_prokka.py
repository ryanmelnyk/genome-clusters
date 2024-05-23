#!/usr/bin/env python3

import sys

limit = int(sys.argv[2])

faa = set()
for line in open("prokka_faa.txt", 'r'):
    if line.startswith("total"):
        continue
    vals = line.rstrip().split()
    faa.add(vals[-1].replace(".faa", ""))

gff = set()
for line in open("prokka_gff.txt", 'r'):
    if line.startswith("total"):
        continue
    vals = line.rstrip().split()
    gff.add(vals[-1].replace(".gff", ""))

if faa != gff:
    print("Amino acid and genbank different! Exiting...")
    sys.exit()

count = 0
missing = set()
for line in open(sys.argv[1], 'r'):
    if line.rstrip() in faa:
        pass
    else:
        missing.add(line.rstrip())
        count += 1
    if count == limit:
        break

o = open("genomes.csv", 'w')
for m in missing:
    o.write(m + "\n")
o.close()

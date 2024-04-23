#!/usr/bin/env python3

o = open("combined_tax.tsv", 'w')

for line in open("old_tax.tsv", 'r'):
    o.write(line)

for line in open("new_tax.tsv", 'r'):
    if line.startswith("user_genome\t"):
        continue
    else:
        o.write(line)
o.close()

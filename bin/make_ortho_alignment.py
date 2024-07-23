#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov

import os
import sys
import string

strains = [line.rstrip() for line in open(sys.argv[1], 'r')]
orthos = [line.rstrip() for line in open("ortholog_groups.txt", 'r')]

align_data = {k: "" for k in strains}
align_genes = {k: {l: None for l in orthos} for k in strains} 

print(f"Creating master alignment...\n")
print(f"Parsing {len(orthos)} orthologs in {len(strains)} strains...")

translation = str.maketrans("","",string.ascii_lowercase+".")

total_leng = 0
count = 0
for o in orthos:
    count += 1
    for line in open(os.path.join("group_hmms", f"{o}.hmm")):
        if line.startswith("LENG"):
            length = int(line.rstrip().split()[1])
            total_leng += length
            break
    for line in open(os.path.join("group_align_orthos", f"{o}.sto")):
        if line.startswith("#") or line.startswith("//"):
            continue
        else:
            vals = line.rstrip().split()
            if len(vals) < 1:
                continue
            else:
                fields = vals[0].split("|")
                if align_genes[fields[1]][o] == None:
                    align_genes[fields[1]][o] = fields[0]
                    align_data[fields[1]] += vals[1].translate(translation)
                elif fields[0] == align_genes[fields[1]][o]:
                    align_data[fields[1]] += vals[1].translate(translation)
                elif fields[0] != align_genes[fields[1]][o]:
                    pass
                else:
                    pass

    for strain in strains:
        if align_genes[strain][o] == None:
            align_data[strain] += "-" * length
        if len("".join(align_data[strain])) != total_leng:
            print(strain, "is short!")
            print(total_leng, len("".join(align_data[strain])))
            print(align_data[strain])
            print(o)
            sys.exit()
    if count % 10 == 0:
        print(f"{count} genomes processed...")
    else:
        pass
print("Done!")
print("Writing alignment...")
out = open("master_alignment.faa", 'w')

for a in align_data:
    out.write(f">{a}\n")
    alignment = align_data[a].upper().replace(".","-")
    out.write(f"{alignment}\n")
out.close()
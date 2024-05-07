#!/usr/bin/env python3

import os
import json
import sys

o = open("results.csv", 'w')
header = [
    "accession",
    "n_contigs",
    "n50",
    "genome_length",
    "busco_single",
    "busco_multi",
    "busco_fragmented",
    "busco_missing"
]
o.write(",".join(header) + "\n")


json_file = f"short_summary.specific.bacteria_odb10.{sys.argv[1]}.busco.json"
output = f"{sys.argv[1]}.busco/{json_file}"
js = json.load(open(output))
vals = [
    sys.argv[1],
    js["results"]["Number of contigs"],
    js["results"]["Contigs N50"],
    js["results"]["Total length"],
    js["results"]["Single copy percentage"],
    js["results"]["Multi copy percentage"],
    js["results"]["Fragmented percentage"],
    js["results"]["Missing percentage"]
]
o.write(",".join([str(x) for x in vals]) + "\n")
o.close()

# delete fasta file if <50% complete or >10% contamination

singles = float(js["results"]["Single copy percentage"])

print(singles)
if singles < 90:
    os.remove(f"{sys.argv[1]}.fna")

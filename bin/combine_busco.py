#!/usr/bin/env python3

import os
import json

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

for f in os.listdir("."):
    if f.endswith(".fna"):
        acc = f.replace(".fna", "")
        print(f)
        json_file = f"short_summary.specific.bacteria_odb10.{acc}.busco.json"
        output = f"{acc}.busco/{json_file}"
        js = json.load(open(output))
        
        vals = [
            acc,
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

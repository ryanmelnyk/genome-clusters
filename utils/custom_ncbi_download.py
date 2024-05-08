#!/usr/bin/env python

import os
import subprocess
import sys

db_path = "/usr2/people/melnyk/genomedb"
max_files = 50000

to_skip = [
    "GCF_002158865.1"
]

print("Getting list of genomes locally...")
local_path = f"{db_path}/ncbi-refseq-raw/"
args = [
    "ls", "-l", local_path
]
o = open("tmp/genome_manifest.txt", 'w')
proc = subprocess.Popen(args, stdout=o)
proc.wait()
o.close()
local_genomes = set()
for line in open("tmp/genome_manifest.txt", 'r'):
    # parses genome id without looking at version number
    if line.startswith("total"):
        continue
    genome = line.rstrip().split()[-1].split(".")[0].split("_")[1]
    local_genomes.add(genome)
print(f"Done! {len(local_genomes)} found in {db_path}")

fh = open(sys.argv[1], 'r')
header = fh.readline().rstrip().replace("#", "").split("\t")

i = 0
downloaded = 0
for line in fh:
    if line.startswith("#"):
        continue
    else:
        vals = dict(zip(header, line.rstrip().split("\t")))
        if vals["assembly_accession"] in to_skip:
            print(f'Skipping {vals["assembly_accession"]}! Blacklisted.')
            continue
        i += 1
        acc = vals["assembly_accession"].split(".")[0].split("_")[1]
        if acc not in local_genomes:
            id_name = vals["assembly_accession"]
            if os.path.basename(vals['ftp_path']) == "na":
                print(f"Processing genome #{i}: na...skipping!")
                continue
            else: 
                print(f"Processing genome #{i}: {id_name}...")

            dest = f"{db_path}/ncbi-refseq-raw/{id_name}.fna.gz"

            full_name = os.path.basename(vals['ftp_path'])
            args = [
                "curl",
                f"{vals['ftp_path']}/{full_name}_genomic.fna.gz",
                "--silent",
                "--output",
                dest
            ]
            proc = subprocess.Popen(args)
            proc.wait()

            if os.stat(dest).st_size < 5000:
                os.remove(dest)
                print("\tDownload failed...skipping")
            else:
                downloaded += 1

        else:
            pass
        if downloaded == max_files:
            break

print(f"{i} genomes processed from input.")
print(f"{downloaded} genomes successfully download")
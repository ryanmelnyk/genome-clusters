#!/usr/bin/env python

import os
import subprocess

db_path = "/usr2/people/melnyk/genomedb"
max_files = 20000

print("Downloading RefSeq assembly summary from NCBI...")
url = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria"
file = "assembly_summary.txt"
args = [
    "curl",
    f"{url}/{file}",
    "--silent",
    "--output",
    "tmp/assembly_summary.txt"
]
proc = subprocess.Popen(args)
proc.wait()
print("Done!")

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
    genome = line.rstrip().split()[-1].split(".")[0]
    local_genomes.add(genome)
print(f"Done! {len(local_genomes)} found in {db_path}")


fh = open("tmp/assembly_summary.txt", 'r')
fh.readline()
header = fh.readline().rstrip().replace("#", "").split("\t")

i = 0
downloaded = 0
for line in fh:
    if line.startswith("#"):
        continue
    else:
        i += 1
        vals = dict(zip(header, line.rstrip().split("\t")))
        acc = vals["assembly_accession"].split(".")[0]
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

print(f"{i} genomes processed in assembly_summary.txt.")
print(f"{downloaded} genomes successfully download")
#!/usr/bin/env python

# Ryan A. Melnyk - RAMelnyk@lbl.gov

import sys
import os
import subprocess

db_path = "/usr2/people/melnyk/genomedb"

accs = {
    k: None for k in [line.rstrip() for line in open(sys.argv[1], 'r')]
}


faa = set()
print("Getting list of faa files...")
for f in os.listdir(f"{db_path}/ncbi-faa"):
    faa.add(f.replace(".faa.gz", ""))

gff = set()
print("Getting list of gff files...")
for f in os.listdir(f"{db_path}/ncbi-gff"):
    gff.add(f.replace(".gff.gz", ""))

count = 0

for x in ["assembly_summary", "genbank_assembly_summary"]:
    for line in open(f"../genome-clusters/tmp/{x}.txt", 'r'):
        if line.startswith("#"):
            continue
        vals = line.rstrip().split("\t")
        if vals[0] in accs and accs[vals[0]] == None:
            accs[vals[0]] = vals[19]
            count += 1
        elif vals[17] in accs and accs[vals[17]] == None:
            accs[vals[17]] = vals[19]
            count += 1
        else:
            pass

faa_downloaded = 0
gff_downloaded = 0
faa_found = 0
gff_found = 0
faa_failed = 0
gff_failed = 0
url_missing = 0

o = open("tmp/failed_accessions.txt", 'w')
for acc in accs:
    if accs[acc] == None:
        print(f"No URL found for {acc}!")
        o.write(f"No URL found for {acc}!\n")
        continue
    full_name = os.path.basename(accs[acc])
    if acc not in faa:
        dest = f"{db_path}/ncbi-faa/{acc}.faa.gz"
        args = [
            "curl",
            f"{accs[acc]}/{full_name}_protein.faa.gz",
            "--silent",
            "--output",
            dest
        ]
        proc = subprocess.Popen(args)
        proc.wait()
        if os.stat(dest).st_size < 5000:
            try:
                os.remove(dest)
            except FileNotFoundError:
                pass    
            print(f"\tDownload failed for {acc}...skipping")
            o.write(f"\tDownload failed for {acc}...skipping\n")
            faa_failed += 1
        else:
            faa_downloaded += 1
    else:
        faa_found += 1

    if acc not in gff:
        dest = f"{db_path}/ncbi-gff/{acc}.gff.gz"
        
        args = [
            "curl",
            f"{accs[acc]}/{full_name}_genomic.gff.gz",
            "--silent",
            "--output",
            dest
        ]
        proc = subprocess.Popen(args)
        proc.wait()
        if os.stat(dest).st_size < 5000:
            os.remove(dest)
            print(f"\tDownload failed for {acc}...skipping")
            o.write(f"\tDownload failed for {acc}...skipping\n")
            gff_failed += 1
        else:
            gff_downloaded += 1
    else:
        gff_found += 1

print("\n\n")

print(f"{count} of {len(accs)} FTP URLs found for input accessions.")

for x in accs:
    if accs[x] == None:
        print(f"\t{x} URL missing!")

print(f"{faa_found} FAA files found in {db_path}.")
print(f"{faa_downloaded} FAA files downloaded.")
print(f"{faa_failed} FAA files failed to download.")

print(f"{gff_found} GFF files found in {db_path}.")
print(f"{gff_downloaded} GFF files downloaded.")
print(f"{gff_failed} GFF files failed to download.")
o.close()
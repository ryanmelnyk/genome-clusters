# genome-clusters

Scripts for cataloguing reference genomes and local genomes from NCBI to facilitate comparative genomics.

## Preparing environment and storage

Currently, these workflows are only set up to run locally on a server using conda.

### set up genome-processing conda environment

```
conda create -n genome-processing
mamba install --no-channel-priority -c bioconda busco -n genome-processing
mamba install --no-channel-priority -c bioconda parallel -n genome-processing

conda activate genome-processing
busco \
  --download_path /usr2/people/melnyk/data/busco_downloads \
  --download bacteria_odb10
```

### set up genome-clustering conda environment

```
conda create -n genome-clustering
mamba install --no-channel-priority -c bioconda mash -n genome-clustering
mamba install --no-channel-priority -c bioconda parallel -n genome-clustering
```

### set up genome-classifying conda environment

```
conda create -n genome-classifying
mamba install --no-channel-priority -c bioconda gtdbtk -n genome-classifying
conda activate genome-classifying
download-db.sh
```

### set up genome-annotating conda environment

```
conda create -n genome-annotating
mamba install --no-channel-priority -c bioconda prokka -n genome-annotating
```

### Set up local storage data

```
mkdir /usr2/people/melnyk/genomedb
mkdir /usr2/people/melnyk/genomedb/ncbi-refseq-raw
mkdir /usr2/people/melnyk/genomedb/metadata
touch /usr2/people/melnyk/genomedb/metadata/genome_stats.csv
touch /usr2/people/melnyk/genomedb/metadata/clusters.csv

mkdir /usr2/people/melnyk/genomedb/custom-raw
touch /usr2/people/melnyk/genomedb/metadata/custom_stats.csv

mkdir /usr2/people/melnyk/genomedb/prokka
mkdir /usr2/people/melnyk/genomedb/prokka/faa
mkdir /usr2/people/melnyk/genomedb/prokka/gff

mkdir /usr2/people/melnyk/genomedb/ncbi-faa
mkdir /usr2/people/melnyk/genomedb/ncbi-gff
```

## Production history

April 30, 2024
  - ran to completion on RefSeq
  - 350,827 total genomes screened
  - 317,652 genomes passing QC
  - 27,321 clusters assigned GTDB taxonomy
  - manually removed bizarre genome GCF_002158865.1
    - see `remove_genomes.ipynb`
    - passed BUSCO filter but was mostly gaps in GTBDtk align

May 22, 2024
  - Added plasmidsaurus strains to custom database
  - download ARLG strains for Kp, Ab, and Pa
  - download everything matching the following species from genbank_assembly_summary.txt
    - Pseudomonas
    - Stutzerimonas
    - Azotobacter
    - Azomonas
    - Entomomonas
    - Ventosimonas
    - Atopomonas
    - Halopseudomonas
    - Thiopseudomonas
    - Azospirillum
  - 375,257 total genomes screened
  - 328,672 genomes passing QC and in `gtdbtk_msa.faa`
  - 27,335 clusters assigned GTDB taxonomy
  - downloaded 26,952 FAA/GFF files for the Pseudomonadaceae clade for pangenomics
  - size of genomedb: 452 Gb


## NCBI Genomes

### Building a database

```
utils/stage_ncbi_assembly_summary.py
```

This will download a summary file of all RefSeq accessions and proceed to download gzipped nucleotide fasta files for each new accession.

Currently, this will skip new versions of existing accessions (i.e. if `GCF_001928625.1` is already downloaded, `GCF_001928625.2` will not be downloaded). This does mean that sometimes improved assemblies are missed (i.e. finished circular).

Also note that occassionally genomes are removed from RefSeq (e.g. https://www.ncbi.nlm.nih.gov/assembly/GCA_001928005.2) for various reasons. These genomes will not have an entry in `assembly_summary.txt` but will stay in the `genomedb`

### Supplementing database with GenBank accessions

You can download an assembly summary file for all Genbank files

```
curl \
  https://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt \
  --output \
  genbank_assembly_summary.txt
```

Parse this file however and remove the first double-commented line. You can then feed the file with the lines you want to `utils/custom_ncbi_download.py`

This will download the appropriate GCA_ files, checking for equivalent GCF_ files in the `genomedb` ncbi-refseq-raw files as well.

### Process

```
nextflow process_genomes.nf
```

This runs BUSCO on all genomes downloaded to `s3://directory/ncbi-refseq-raw` to assess completeness and quality. It will terminate after the `stage_aws` process if all genomes have an entry in `directory/metadata/genome_stats.csv`

When processes fail this is usually due to incompletely downloaded fasta files - a check has been added to `stage_ncbi_assembly_summary.py` to delete very small files (usually an XML curl error).

To find failed jobs after run is over:
```
grep "exit: 1" .nextflow.log | grep "DEBUG" | less -S
```

### Cluster

If `centroids.msh` doesn't exist and you haven't run `cluster_genomes.nf` use the `--initialize` parameter like so.
```
nextflow cluster_genomes.nf --initialize
```
Note that if you re-run using the initialize flag, it will overwrite any existing data in the `genomedb` folder! Be careful.

Once the metadata files have been created, run using no `--initialize` parameter

This will run MASH to cluster genomes passing QC iteratively into 95% centroids. Passing QC is defined has having >90% of the 124 BUSCO genes as single copies and having an N50 > 20000. I may want to revisit this threshold - there seem to be a lot of genomes smaller than 2 Mb that have ~88% or so single copy genes.

Note that these centroids are not perfect or robust - I use a simple 95% threshold match to existing centroids to classify genomes. This is simply to dereplicate the large NCBI genome database to get rough taxonomies prior to more focused analyses Something like dRep is more appropriate that uses FastANI for fine-grained resolutions.

This will fail if there are no new genomes to cluster, i.e. all genomes passing QC from `genome_stats.csv` have an entry in `clusters.csv`.

```
for i in {1..5}; do nextflow cluster_genomes.nf --cpus 4; done
```

### Classify

Runs GTDB on centroids.

If you haven't run GTDB using this genomedb before, run:
```
nextflow classify_genomes.nf --initialize
```

Since GTDB has been updated to v2 the memory requirement for the pplacer step has decreased substantially. It's now possible to run using no more than 128 GB of RAM. However, this is still a computationally expensive process for large #s of genomes. Running on 10K genomes using 16 CPUs takes over 24 hours.

100 genomes - 1.5 hrs using 16 CPUs
10000 genomes - 38.5 hrs using 16 CPUs
1000 genomes - 5.2 hrs using 16 CPUs
1000 genomes - 4.7 hrs using 16 CPUs
3000 genomes - 12 hrs using 16 cpus

GCF_002158865.1 failed GTDBtk - it passed the initial busco filtering step but only had ~3% or so of the amino acids needed for gtdbtk. Not sure what the discrepancy is but it would be ideal to filter this out of all output files, including the mash centroid file (yuck).

Ideally, wait until all centroids are processed through GTDBtk before dealing with updating the databases.

Done - this process is detailed in `ipynb/remove_genomes.ipynb`.

### Align Only

Generate alignment data for all NCBI strains, not just centroids. Takes a lot less time than doing phylogenetic placement and classification.

```
nextflow align_genomes_only.nf
```

10000 files, 12 cpus - 6.25 hrs
5000 files, 12 cpus - 2.75 hrs
50000 files, 8 cpus - 46 hours

```
for i in {1..10}; do echo "Iteration" $i "running..."; nextflow align_genomes_only.nf --cpus 8; make clean; done
```


### Updating database quickstart

```
utils/stage_ncbi_assembly_summary.py
nextflow process_genomes.nf
nextflow cluster_genomes.nf
nextflow classify_genomes.nf

nextflow align_genomes_only.nf
```

### Build a reference phylogeny for centroids

```
utils/centroid_align.py
conda activate genome-classifying
FastTree tmp/centroid_msa.faa > tmp/centroid_msa.tre
```

```
conda activate base
utils/rename_centroid_tree.py \
  tmp/centroid_msa.tre \
  tmp/centroid_msa.renamed.tre

scp /usr2/people/melnyk/genome-clusters/tmp/centroid_msa.renamed.tre trees/240522_centroid.tre
```

## Custom Genomes

### Downloading additional genomes from NCBI GenBank

download genbank assembly summary

```
curl \
  https://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt \
  --output \
  tmp/genbank_assembly_summary.txt
```
 
### Preparing custom genomes for processing

Start from scratch with just the gzipped nucleotide FASTA file (same as NCBI). Name each strain using some unique strain identifier.


Note that there is no automatic check for same-named strains at this time. Name the files accurately as everything before the first period becomes the identifying string for all downstream data (e.g. MRSN123456789.fna, PAO1_AMD2627.fna).

The first time running this on custom (non-NCBI) genomes use the `--initialize` parameter

```
nextflow custom_genomes.nf --initialize
```

## Comparative genomics



### downloading faa and gff files
```
utils/download_faa_gff.py tmp/pseudo_cent_accessions.txt
```


```
utils/download_faa_gff.py tmp/pseudo_cluster_accessions.txt
```

### Installing pangenome module

use recipe from PIRATE with a few additional tweaks

```
conda create -n pirate

mamba install \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    pirate \
    -n pirate

conda activate pirate
pip install Bio
```


### Running Prokka for clades of interest

Running Prokka seems to be necessary for using certain pangenome tools as the NCBI-formatted GFF/GBK files are not formatted correctly.

This can be done by generating a list of accession IDs, e.g. 
```
GCF_900105655.1
GCF_036960865.1
GCF_900105255.1
GCF_003797945.1
```

```
nextflow annotate_genomes.nf \
  --input_csv tmp/pseudo_cluster_accessions.txt \
  --cpus 6 \
  --file_limit 30000
```
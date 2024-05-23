#!/usr/bin/env nextflow

params.genomedb = "/usr2/people/melnyk/genomedb"

process stage_prokka {
  cpus 1
  memory '1.5 GB'
  conda '/usr2/people/melnyk/.conda/envs/my_base'
  tag "stage_prokka"

  input:
  path(genomes)

  output:
  path "genomes.csv", emit: csv

  script:
  """

  ls -l ${params.genomedb}/prokka/faa > prokka_faa.txt

  ls -l ${params.genomedb}/prokka/gff > prokka_gff.txt

  parse_prokka.py ${genomes} ${params.file_limit}
  """

}

process run_prokka {
  cpus 1
  memory '12 GB'
  maxForks params.cpus
  conda '/usr2/people/melnyk/.conda/envs/genome-annotating'
  tag "${accession}"

  input:
  val(accession)

  output:

  script:
  """
  ln -s ${params.genomedb}/ncbi-refseq-raw/${accession}.fna.gz .

  gunzip -f ${accession}.fna.gz

  prokka \
    --outdir PROKKA \
    --prefix PROKKA \
    --centre XXX \
    --compliant \
    --cpus 1 \
    ${accession}.fna

  mv PROKKA/PROKKA.faa ${accession}.faa
  mv PROKKA/PROKKA.gff ${accession}.gff

  cp \
    ${accession}.faa \
    ${params.genomedb}/prokka/faa/${accession}.faa

  cp \
    ${accession}.gff \
    ${params.genomedb}/prokka/gff/${accession}.gff
  """

}

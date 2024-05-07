#!/usr/bin/env nextflow

params.genomedb = "/usr2/people/melnyk/genomedb"
params.busco_downloads = "/usr2/people/melnyk/data/busco_downloads"

process stage_aws {
  cpus 1
  memory '1.5 GB'
  conda '/usr2/people/melnyk/.conda/envs/my_base'
  tag "stage_genomes"

  input:

  output:
  path "genomes.csv", emit: csv

  script:
  """
  ls -l ${params.genomedb}/ncbi-refseq-raw > local_manifest.txt

  cp ${params.genomedb}/metadata/genome_stats.csv .

  parse_aws.py ${params.file_limit}
  """

}

process stage_custom {
  cpus 1
  memory '1.5 GB'
  conda '/usr2/people/melnyk/.conda/envs/my_base'
  tag "stage_genomes"

  input:

  output:
  path "genomes.csv", emit: csv

  script:
  """
  ls -l ${params.genomedb}/custom-raw > local_manifest.txt

  cp ${params.genomedb}/metadata/custom_stats.csv .

  parse_aws_custom.py ${params.file_limit}
  """

}


process download_and_qc {
  cpus 1
  memory '1.8 GB'
  conda '/usr2/people/melnyk/.conda/envs/genome-processing'
  maxForks params.cpus
  tag "download_genomes_${iter}"
  errorStrategy 'ignore'

  input:
  val(genomes)
  val(iter)

  output:
  path "results.csv", emit: csv

  script:
  cmd = ""

  for (g in genomes) {
    cmd += """
    ln -s ${params.genomedb}/ncbi-refseq-raw/${g}.fna.gz .
    gunzip -f ${g}.fna.gz
    busco \
      -i ${g}.fna \
      -l bacteria_odb10 \
      --offline \
      -c 1 \
      --download_path ${params.busco_downloads} \
      -o ${g}.busco \
      -m genome
    """
  }

  cmd += """
  combine_busco.py

  rm *.fna
  rm -r *.busco
  """

  cmd
}

process process_custom {
  cpus 1
  memory '3.6 GB'
  conda '/usr2/people/melnyk/.conda/envs/genome-processing'
  tag "download_genomes_${iter}"
  maxForks params.cpus

  input:
  val(prefix)

  output:
  path "results.csv", emit: csv
  path "${prefix}.fna", emit: fasta, optional: true

  script:
  cmd = """
  echo ${prefix}

  cp \
    ${params.genomedb}/custom-raw/${prefix}.fna.gz \
    .
  gunzip ${prefix}.fna.gz

  busco \
    -i ${prefix}.fna \
    -l bacteria_odb10 \
    -c 1 \
    --offline \
    --download_path ${params.busco_downloads} \
    -o ${prefix}.busco \
    -m genome

  parse_busco.py ${prefix}

  """

}

process combine_results {
  cpus 1
  memory '4 GB'
  conda '/usr2/people/melnyk/.conda/envs/genome-processing'
  tag { 'combine_results' }

  input:
  path "*.csv"

  output:

  script:
  """
  cp ${params.genomedb}/metadata/genome_stats.csv old_genome_stats.csv

  combine_csvs.py

  cp genome_stats.csv ${params.genomedb}/metadata/genome_stats.csv
  """

}

process combine_results_custom {
  cpus 1
  memory '4 GB'
  conda '/usr2/people/melnyk/.conda/envs/genome-processing'
  tag { 'combine_results' }

  input:
  path "*.csv"

  output:

  script:
  """
  cp ${params.genomedb}/metadata/custom_stats.csv old_custom_stats.csv

  combine_csvs.py

  cp genome_stats.csv ${params.genomedb}/metadata/custom_stats.csv
  """

}

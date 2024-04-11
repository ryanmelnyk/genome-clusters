#!/usr/bin/env nextflow

params.genomedb = "/usr2/people/melnyk/genomedb"
params.busco_downloads = "/usr2/people/melnyk/data/busco_downloads"
params.forks = 8

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

// process stage_custom {
//   cpus 1
//   memory '1.5 GB'
//   conda '/usr2/people/melnyk/.conda/envs/my_base'
//   tag "stage_genomes"

//   input:

//   output:
//   path "genomes.csv", emit: csv

//   script:
//   """
//   aws s3 ls \
//     s3://directory/custom-raw/ > aws_manifest.txt

//   aws s3 cp \
//     s3://directory/metadata/custom_stats.csv \
//     .

//   aws s3 cp \
//     s3://directory/metadata/custom_taxonomy.tsv \
//     .

//   parse_aws_custom.py ${params.file_limit}
//   """

// }


process download_and_qc {
  cpus 1
  memory '1.8 GB'
  conda '/usr2/people/melnyk/.conda/envs/genome-processing'
  maxForks params.forks
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
    cp ${params.genomedb}/ncbi-refseq-raw/${g}.fna.gz .
    gunzip ${g}.fna.gz
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

// process process_custom {
//   cpus 2
//   memory '3.6 GB'
//   conda '/home/ec2-user/miniconda3/envs/genome-processing/'
//   tag "download_genomes_${iter}"
//   // errorStrategy  { task.attempt <= maxRetries  ? 'retry' : 'ignore' }
//   // maxRetries 3
//   maxForks params.forks

//   input:
//   val(prefix)

//   output:
//   path "results.csv", emit: csv
//   path "${prefix}.fna", emit: fasta, optional: true

//   script:
//   cmd = """
//   echo ${prefix}

//   aws s3 cp \
//     s3://directory/custom-raw/${prefix}.fna.gz \
//     .
//   gunzip ${prefix}.fna.gz

//   busco \
//     -i ${prefix}.fna \
//     -l bacteria_odb10 \
//     -c 2 \
//     --offline \
//     --download_path ${params.busco_downloads} \
//     -o ${prefix}.busco \
//     -m genome

//   parse_busco.py ${prefix}

//   """

// }

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

// process combine_results_custom {
//   cpus 1
//   memory '4 GB'
//   conda '/home/ec2-user/miniconda3/envs/genome-processing/'
//   tag { 'combine_results' }

//   input:
//   path "*.csv"

//   output:

//   script:
//   """
//   aws s3 cp \
//     s3://directory/metadata/custom_stats.csv \
//     old_custom_stats.csv

//   combine_csvs.py

//   aws s3 cp \
//     genome_stats.csv \
//     s3://directory/metadata/custom_stats.csv
//   """

// }

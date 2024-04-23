#!/usr/bin/env nextflow
params.genomedb = "/usr2/people/melnyk/genomedb"

process stage_genomes {
  cpus 1
  memory '1.5 GB'
  conda '/usr2/people/melnyk/.conda/envs/my_base'
  tag "stage_genomes"

  input:

  output:
  path "genomes.csv", emit: csv

  script:
  cmd = ""
  
  cmd += """
  ls -l ${params.genomedb}/ncbi-refseq-raw > aws_manifest.txt

  cp ${params.genomedb}/metadata/clusters.csv .
  """

  if (params.initialize) {
    cmd += """
    touch ${params.genomedb}/metadata/gtdbtk_taxonomy.tsv
    """
  }

  cmd += """
  cp ${params.genomedb}/metadata/gtdbtk_taxonomy.tsv .

  parse_genome_clusters.py ${params.file_limit}
  """

  cmd
}

// process stage_genomes_align_only {
//   cpus 1
//   memory '1.5 GB'
//   conda '/usr2/people/melnyk/.conda/envs/my_base'
//   tag "stage_genomes"

//   input:

//   output:
//   path "genomes.csv", emit: csv

//   script:
//   """
//   ls -l ${params.genomedb}/ncbi-refseq-raw > aws_manifest.txt

//   cp ${params.genomedb}/metadata/clusters.csv .

//   cp ${params.genomedb}/metadata/gtdbtk_msa.faa .

//   parse_genome_clusters_align_only.py ${params.file_limit}
//   """

// }


process classify_genomes {
  cpus params.cpus
  memory "60 GB"
  conda '/usr2/people/melnyk/.conda/envs/genome-classifying'
  tag { 'classify_genomes' }

  input:
  path(genomes)

  output:

  script:
  cmd = ""

  if (!params.initialize) {
    cmd += """
    cp ${params.genomedb}/metadata/gtdbtk_msa.faa old_msa.faa

    cp ${params.genomedb}/metadata/gtdbtk_taxonomy.tsv old_tax.tsv
    """
  }
  
  cmd += """
  mkdir genomes
  cat genomes.csv | xargs -I % ln -s ${params.genomedb}/ncbi-refseq-raw/% genomes

  gtdbtk identify \
    --genome_dir genomes \
    --out_dir identify \
    --cpus ${params.cpus} \
    --extension gz

  gtdbtk align \
    --identify_dir identify \
    --out_dir align \
    --skip_gtdb_refs \
    --cpus ${params.cpus}

  gtdbtk classify \
    --genome_dir genomes \
    --out_dir classify \
    --align_dir align \
    --skip_ani_screen \
    --extension gz \
    --cpus ${params.cpus}
  """

  if (!params.initialize) {
    cmd += """
    mv align/align/gtdbtk.bac120.user_msa.fasta.gz new_msa.faa.gz
    gunzip new_msa.faa.gz
    cat old_msa.faa new_msa.faa > combined_msa.faa

    mv classify/classify/gtdbtk.bac120.summary.tsv new_tax.tsv

    combine_tax.py

    cp combined_msa.faa ${params.genomedb}/metadata/gtdbtk_msa.faa

    cp combined_tax.tsv ${params.genomedb}/metadata/gtdbtk_taxonomy.tsv
    """
  }

  if (params.initialize) {
    cmd += """
    mv align/align/gtdbtk.bac120.user_msa.fasta.gz new_msa.faa.gz
    gunzip new_msa.faa.gz

    cp new_msa.faa ${params.genomedb}/metadata/gtdbtk_msa.faa
    mv classify/classify/gtdbtk.bac120.summary.tsv new_tax.tsv
    cp new_tax.tsv ${params.genomedb}/metadata/gtdbtk_taxonomy.tsv
    """
  }

  cmd
}

// process align_genomes {
//   cpus params.cpus
//   memory "60 GB"
//   conda '/usr2/people/melnyk/.conda/envs/genome-classifying'
//   tag { 'align_genomes' }

//   input:
//   path(genomes)

//   output:

//   script:
//   """
//   aws s3 cp \
//     ${aws_url}/metadata/gtdbtk_msa.faa \
//     old_msa.faa

//   mkdir genomes
//   parallel \
//     -j ${params.cpus} \
//     -a genomes.csv \
//     aws s3 cp ${aws_url}/ncbi-refseq-raw/{} genomes

//   gtdbtk identify \
//     --genome_dir genomes \
//     --out_dir identify \
//     --cpus ${params.cpus} \
//     --extension gz

//   gtdbtk align \
//     --identify_dir identify \
//     --out_dir align \
//     --skip_gtdb_refs \
//     --cpus ${params.cpus}

//   mv align/align/gtdbtk.bac120.user_msa.fasta.gz new_msa.faa.gz
//   gunzip new_msa.faa.gz
//   cat old_msa.faa new_msa.faa > combined_msa.faa

//   aws s3 cp \
//      combined_msa.faa \
//     ${aws_url}/metadata/gtdbtk_msa.faa
//   """

// }

// process classify_genomes_custom {
//   cpus params.cpus
//   memory "60 GB"
//   conda '/usr2/people/melnyk/.conda/envs/genome-classifying'
//   tag { 'cluster_genomes' }

//   input:
//   path(genomes)

//   output:

//   script:
//   """
//   mkdir genomes
//   mv *.fna genomes
//   aws s3 cp \
//     ${aws_url}/metadata/custom_msa.faa \
//     old_msa.faa

//   aws s3 cp \
//     ${aws_url}/metadata/custom_taxonomy.tsv \
//     old_tax.tsv

//   gtdbtk identify \
//     --genome_dir genomes \
//     --out_dir identify \
//     --cpus ${params.cpus} \
//     --extension fna

//   gtdbtk align \
//     --identify_dir identify \
//     --out_dir align \
//     --skip_gtdb_refs \
//     --cpus ${params.cpus}

//   gtdbtk classify \
//     --genome_dir genomes \
//     --out_dir classify \
//     --align_dir align \
//     --extension fna \
//     --cpus ${params.cpus}

//   mv align/align/gtdbtk.bac120.user_msa.fasta.gz new_msa.faa.gz
//   gunzip new_msa.faa.gz

//   cat old_msa.faa new_msa.faa > combined_msa.faa

//   mv classify/classify/gtdbtk.bac120.summary.tsv new_tax.tsv
//   combine_tax.py

//   aws s3 cp \
//     combined_msa.faa \
//     ${aws_url}/metadata/custom_msa.faa

//   aws s3 cp \
//     combined_tax.tsv \
//     ${aws_url}/metadata/custom_taxonomy.tsv

//   """

// }

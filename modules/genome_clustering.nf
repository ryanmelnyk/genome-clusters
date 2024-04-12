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
  """
  ls -l ${params.genomedb}/ncbi-refseq-raw > aws_manifest.txt

  cp ${params.genomedb}/metadata/genome_stats.csv .

  cp ${params.genomedb}/metadata/clusters.csv .

  parse_genome_stats.py ${params.file_limit}
  """

}

process cluster_genomes {
  cpus params.cpus
  conda '/usr2/people/melnyk/.conda/envs/genome-clustering'
  tag { 'cluster_genomes' }

  input:
  path(genomes)

  output:

  script:
  cmd = ""

  if (!params.initialize) {
    cmd += """
    cp ${params.genomedb}/metadata/clusters.csv old_clusters.csv

    cp ${params.genomedb}/metadata/centroids.msh old_centroids.msh
    """
  }

  cmd += """
  parallel \
    -j ${params.disk_cpus} \
    -a genomes.csv \
    ln -s ${params.genomedb}/ncbi-refseq-raw/{} .

  parallel -j ${params.disk_cpus} gunzip -f ::: *.fna.gz

  ls *.fna > fasta_list.txt

  mash sketch \
    -p ${params.cpus} \
    -l fasta_list.txt \
    -o new_all.msh
  """

  if (!params.initialize) {
    cmd += """
    mash paste \
      combined \
      old_centroids.msh \
      new_all.msh

    mash dist \
      -d 0.05 -p ${params.cpus} \
      combined.msh \
      new_all.msh > new_dist.txt
    """
  }

  if (params.initialize) {
    cmd += """
    mash dist \
      -d 0.05 -p ${params.cpus} \
      new_all.msh \
      new_all.msh > new_dist.txt

    touch old_clusters.csv
    """
  }
  
  cmd += """
  parse_new_mash.py

  mash sketch \
    -p ${params.cpus} \
    -l new_centroid_list.txt \
    -o new_centroids.msh

  rm *.fna
  """

  if (!params.initialize) {
    cmd += """
    mash paste \
      combined_centroids \
      old_centroids.msh \
      new_centroids.msh
    
    cp combined_clusters.csv ${params.genomedb}/metadata/clusters.csv
    cp combined_centroids.msh ${params.genomedb}/metadata/centroids.msh
    rm *.msh
    """
  }

  if (params.initialize) {
  cmd += """
  cp combined_clusters.csv ${params.genomedb}/metadata/clusters.csv
  cp new_centroids.msh ${params.genomedb}/metadata/centroids.msh
  rm *.msh
  """
  }

  cmd
}

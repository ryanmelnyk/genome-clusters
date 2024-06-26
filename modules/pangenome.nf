#!/usr/bin/env nextflow

params.genomedb = "/usr2/people/melnyk/genomedb"

process diamond_mcl_inf_gradient {
  cpus params.cpus
  memory '8 GB'
  conda '/usr2/people/melnyk/.conda/envs/pirate'
  tag "stage_faa"

  input:
  path(genomes)

  output:

  script:
  cmd = """
  cp ${genomes} genomes.txt
  cat genomes.txt | xargs -I % ln -s ${params.genomedb}/ncbi-faa/%.faa.gz
  parallel -j ${params.cpus} gunzip -f ::: *.faa.gz

  nstrains=\$(ls | grep ".faa" | wc -l)
  echo \$((\$nstrains*2))

  rename_faa.py genomes.txt

  cat genomes.txt | xargs -I % rm %.faa

  mmseqs easy-linclust \
    combined.faa \
    mmseqs95 \
    tmp_mmseqs \
    --threads ${params.cpus} \
    --split-memory-limit 200G \
    --min-seq-id 0.95 \
    -c 0.95 \
    --cov-mode 0

  diamond makedb \
    --in mmseqs95_rep_seq.fasta \
    -d clustered.dmnd \
    --threads ${params.cpus}

  mkdir tmp_dmnd
  diamond blastp \
    --query mmseqs95_rep_seq.fasta \
    -d clustered.dmnd \
    -t tmp_dmnd \
    -o diamond.m8 \
    -f tab \
    --max-target-seqs \$((\$nstrains*2)) \
    --min-score 50 \
    --threads ${params.cpus}

  parse_diamond.py mmseqs95_rep_seq.fasta diamond.m8

  mcxload \
    --stream-mirror \
    --write-binary \
    -abc input.abc \
    -o data.mci \
    -write-tab data.tab

  mcl data.mci -te ${params.cpus} -I 1.2
  mcl data.mci -te ${params.cpus} -I 1.4
  mcl data.mci -te ${params.cpus} -I 1.6
  mcl data.mci -te ${params.cpus} -I 1.8
  mcl data.mci -te ${params.cpus} -I 2
  mcl data.mci -te ${params.cpus} -I 4
  mcl data.mci -te ${params.cpus} -I 6
  mcl data.mci -te ${params.cpus} -I 8

  mcxdump -imx data.mci -icl out.data.mci.I12 -tabr data.tab -o clusters.I12.txt
  mcxdump -imx data.mci -icl out.data.mci.I14 -tabr data.tab -o clusters.I14.txt
  mcxdump -imx data.mci -icl out.data.mci.I16 -tabr data.tab -o clusters.I16.txt
  mcxdump -imx data.mci -icl out.data.mci.I18 -tabr data.tab -o clusters.I18.txt
  mcxdump -imx data.mci -icl out.data.mci.I20 -tabr data.tab -o clusters.I20.txt
  mcxdump -imx data.mci -icl out.data.mci.I40 -tabr data.tab -o clusters.I40.txt
  mcxdump -imx data.mci -icl out.data.mci.I60 -tabr data.tab -o clusters.I60.txt
  mcxdump -imx data.mci -icl out.data.mci.I80 -tabr data.tab -o clusters.I80.txt

  parse_clusters.py clusters.I12.txt mmseqs95_cluster.tsv
  parse_clusters.py clusters.I14.txt mmseqs95_cluster.tsv
  parse_clusters.py clusters.I16.txt mmseqs95_cluster.tsv
  parse_clusters.py clusters.I18.txt mmseqs95_cluster.tsv
  parse_clusters.py clusters.I20.txt mmseqs95_cluster.tsv
  parse_clusters.py clusters.I40.txt mmseqs95_cluster.tsv
  parse_clusters.py clusters.I60.txt mmseqs95_cluster.tsv
  parse_clusters.py clusters.I80.txt mmseqs95_cluster.tsv
  """

}

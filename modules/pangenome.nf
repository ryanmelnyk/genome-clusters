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
  echo \$((\$nstrains*10))

  rename_faa.py

  cd-hit \
    -M 8000 \
    -T ${params.cpus} \
    -c 0.95 \
    -i combined.faa \
    -d 0 \
    -l 50 \
    -o clustered.faa

  cat genomes.txt | xargs -I % rm %.faa

  diamond makedb \
    --in clustered.faa \
    -d clustered.dmnd \
    --threads ${params.cpus}

  mkdir tmp
  diamond blastp \
    --query clustered.faa \
    -d clustered.dmnd \
    -t tmp \
    -o diamond.m8 \
    -f tab \
    --max-target-seqs \$((\$nstrains*10)) \
    --min-score 50 \
    --threads ${params.cpus}

  parse_diamond.py

  mcxload \
    --stream-mirror \
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

  parse_clusters.py clusters.I12.txt
  parse_clusters.py clusters.I14.txt
  parse_clusters.py clusters.I16.txt
  parse_clusters.py clusters.I18.txt
  parse_clusters.py clusters.I20.txt
  parse_clusters.py clusters.I40.txt
  parse_clusters.py clusters.I60.txt
  parse_clusters.py clusters.I80.txt
  """

}

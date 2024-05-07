#!/usr/bin/env nextflow
params.file_limit = 5000
params.cpus = 8
params.initialize = false

include {
  stage_custom;
  process_custom;
  combine_results_custom
} from "./modules/genome_processing.nf"

include { classify_genomes_custom } from "./modules/genome_classifying.nf"

workflow {

  stage_custom()

  process_custom(
    stage_custom.out.csv.splitCsv().map { row -> row[0] }
    )

  combine_results_custom(
      process_custom.out.csv.collect()
    )

  classify_genomes_custom(
      process_custom.out.fasta.collect()
    )

}

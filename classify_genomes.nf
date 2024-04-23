#!/usr/bin/env nextflow
params.file_limit = 10000
params.cpus = 16
params.initialize = false

include {
  stage_genomes;
  classify_genomes
} from "./modules/genome_classifying.nf"


workflow {

  stage_genomes()

  classify_genomes(stage_genomes.out.csv)

}

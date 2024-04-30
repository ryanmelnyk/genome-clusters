#!/usr/bin/env nextflow
params.file_limit = 1000
params.cpus = 12

include {
  stage_genomes_align_only;
  align_genomes
} from "./modules/genome_classifying.nf"


workflow {

  stage_genomes_align_only()

  align_genomes(stage_genomes_align_only.out.csv)

}

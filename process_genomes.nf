#!/usr/bin/env nextflow

params.file_limit = 50000
params.file_collate = 20
params.cpus = 12

include {
  stage_aws;
  download_and_qc;
  combine_results
} from "./modules/genome_processing.nf"


workflow {

  stage_aws()

  download_and_qc(
    stage_aws.out.csv
      .splitCsv()
      .map { row -> row[0] }
      .collate(params.file_collate),
    Channel.from(1..(params.file_limit/params.file_collate) + 2)
  )

  combine_results(
      download_and_qc.out.collect()
    )



}

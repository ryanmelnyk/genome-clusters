#!/usr/bin/env nextflow
params.input_csv = "test/test.csv"
params.file_limit = 100
params.cpus = 8


include {
  stage_prokka;
  run_prokka
} from "./modules/genome_annotating.nf"


workflow {

  stage_prokka(channel.fromPath(params.input_csv))

  input_files = stage_prokka.out.csv
    .splitCsv()
    .map { row -> row[0] }

  run_prokka(input_files)

}

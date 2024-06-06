#!/usr/bin/env nextflow
params.cpus = 8
params.input_csv = "test/test_pangenome.txt"

include {
  diamond_mcl_inf_gradient;
} from "./modules/pangenome.nf"

workflow {

  diamond_mcl_inf_gradient(channel.fromPath(params.input_csv))

}

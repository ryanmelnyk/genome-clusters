
params.file_limit = 10000
params.cpus = 16
params.disk_cpus = 4
params.initialize = false

include {
  stage_genomes;
  cluster_genomes
} from "./modules/genome_clustering.nf"


workflow {

  stage_genomes()

  cluster_genomes(stage_genomes.out.csv)

}

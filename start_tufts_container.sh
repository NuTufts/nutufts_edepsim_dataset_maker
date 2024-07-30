#!/bin/bash

module load singularity/3.5.3
singularity shell -B /tmp:/tmp,/cluster,/cluster /cluster/tufts/wongjiradlabnu/larbys/larbys-container/simpledet_petastorm_u20.04_geant4.10.06.p03.sif

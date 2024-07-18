# Container recipe

To run the different parts of the code to make data sets, we need the following:

* Geant4 (and its dependencies): this software library is the standard tool for modeling how different particles travel through the matter.
* EDepSim (included in this repository): Geant4 is only a library of algorithms for setting up a particle simulation.  EDepSim is an application focused on making particular simulations of particles going through liquid argon.
* ROOT (and its dependencies): this is a software library used by EDepSim to store the output of its simulation.
* simpledet (custom code in this repository): an overly simple model of a LArTPC detector that produces the data "images" from our simulated detector.
* petastorm (and its dependencies pyarrow and pyspark): a library to build pyspark databases that can stores numpy arrays and other information into a database table. Comes with functions to also create a pytorch dataset and dataloader which we can use to load our data during training of various models.

Our container is built through stages to provide certain libraries (and their dependencies):

* Base container is ubuntu 20.04 (currently)
* The next stage involves installing ROOT v6.24.02). Defining container image `larbys/root:v6.24.03_u20.04` available on dockerhub.
* The next stage involves installing Geant4 v4.10.06.p03
* We then install various ML-focused python libraries: numpy, scipy, plotly, matplotlib, pytorch (with gpu support), pyspark, pyarrow, and petastorm

The intention is to have a ready-made container for running code to create training images.

Dockerfiles in this folder:

* Dockerfile_u20.02_geant4.10.06.p03: takes us up the next to last stage.
* Dockerfile_petastorm: the final container stage
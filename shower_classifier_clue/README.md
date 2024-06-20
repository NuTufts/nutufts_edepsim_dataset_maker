# Shower Classifier CLUE

These are scripts to make the data sets for exploring uncertainty quantification using ideas from the CLUE paper.

Our test case is a classifier separating three particle types:

* electrons
* photons
* e+/e- pairs produced according to some dark sector model

### Proof of principle dataset

To do proof of principle studies, we'll start with images that remove some degrees of freedom that are not important to testing out the ideas of this project.

We will:

* generate images such that the showers start at the same point in the image
* keep the total momenta along the same axis

We will need to keep the following meta-data
* particle type
* initial momentum
* energy deposit information near the trunk
* keypoints to help describe the structure somehow? photon conversion or compton scattering points maybe.

We will save the info using Petastorm repository.
This is based on pyspark and provides a fairly convenient way to load data into the network.
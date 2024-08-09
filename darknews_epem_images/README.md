# Project folder for making Images for Dark Neutrino Interactions

Uses DarkNews

## Example workflow

First step is to generate some interactions using DarkNews

```
Steps from Kenna here
```

Next, we pass those events to `edep-sim`, which uses the Geant4 library to simulate what the output particles of our interactions will do when moving through a block of liquid argon.

```
edep-sim -g larblock.gdml -o test_epem.root -e 2 hepevt_example.mac
```
where:
* `larblock.gdml` is a file that defines the "detector" geometry. It is just a rectangular block of liquid argon.
* `hepevt_example.mac` is a "macro" file, configuration edep-sim/geant4

We then use `simpledet` to turn the information from the simulation into an image along with meta-data from the sim.
The info is stored in an hdf5 file.

```
python3 run_edepsim2hdf5.py --input-edepsim test_epem.root --out-hdf5 outtest.hdf5 --start-index 0 --class-index 2 -ow
```

As an example of loading such hdf5 files, we can run the following test script to confirm it's content.

```
python3 test_hdf5_dataloader.py --input outtest.hdf5 -n 3
```

You should see something like:
```
Number of entries in the data loader:  1
batch_size= 2
--------------------------------------
iteration[ 0 ] batchidx[ 0 ]
torch.Size([2, 256, 256])
[ 0 ] sum= tensor(258.2114)  img>0.05= tensor(644)
[ 1 ] sum= tensor(123.0773)  img>0.05= tensor(298)
labels:  tensor([2, 2])
--------------------------------------
iteration[ 1 ] batchidx[ 0 ]
torch.Size([2, 256, 256])
[ 0 ] sum= tensor(258.2114)  img>0.05= tensor(644)
[ 1 ] sum= tensor(123.0773)  img>0.05= tensor(298)
labels:  tensor([2, 2])
--------------------------------------
iteration[ 2 ] batchidx[ 0 ]
torch.Size([2, 256, 256])
[ 0 ] sum= tensor(123.0773)  img>0.05= tensor(298)
[ 1 ] sum= tensor(258.2114)  img>0.05= tensor(644)
labels:  tensor([2, 2])
--------------------------------------
iteration[ 3 ] batchidx[ 0 ]
torch.Size([2, 256, 256])
[ 0 ] sum= tensor(258.2114)  img>0.05= tensor(644)
[ 1 ] sum= tensor(123.0773)  img>0.05= tensor(298)
labels:  tensor([2, 2])
--------------------------------------
iteration[ 4 ] batchidx[ 0 ]
torch.Size([2, 256, 256])
[ 0 ] sum= tensor(258.2114)  img>0.05= tensor(644)
[ 1 ] sum= tensor(123.0773)  img>0.05= tensor(298)
labels:  tensor([2, 2])
closing ... (pause to allow dataloader threads to finish)
fin
```

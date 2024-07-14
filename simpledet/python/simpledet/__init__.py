from __future__ import print_function
import ROOT,os

simpledet_dir = os.environ['SIMPLEDET_LIB_DIR']
# We need to load in order
for l in [x for x in os.listdir(simpledet_dir) if x.endswith('.so')]:
    print("load simplet lib: ",l)
    ROOT.gSystem.Load(l)
from ROOT import simpledet


import os,sys

import ROOT as rt
from simpledet import simpledet

IEdepSim = simpledet.edepsim.EDepSimInterface()
print(IEdepSim)

inputfile = rt.TFile("test.root","open")
edeptree = inputfile.Get("EDepSimEvents")

nentries = edeptree.GetEntries()

c1 = rt.TCanvas("c1","",800,600)

for ientry in range(nentries):

    edeptree.GetEntry(ientry)

    seghit_v = edeptree.Event.SegmentDetectors["drift"]
    print("number of seghits: ",seghit_v.size())
    himage = IEdepSim.processSegmentHits( seghit_v )
    print("himage: ",himage)
    himage.Draw("colz")
    c1.Update()
    print("[ENTER] to continue")
    input()
    break





import os,sys
import argparse

parser = argparse.ArgumentParser(
    prog='test_save2petasormdb.py',
    description='Example/Test saving simpledet image into petastorm DB.',
    epilog='Text at the bottom of help')

parser.add_argument('--input-edepsim', '-i', required=True, type=str,
                    help='path to input edepsim file')
parser.add_argument('--petastorm-db-folder', '-db', required=True, type=str,
                    help='If output-format is "petastorm", this argument is required in order to set the location to the petastorm database folder.')
parser.add_argument('--tag', '-t', required=True, type=str,
                    help='label for partition in database')

cropsize = 256

args = parser.parse_args()

# we need ROOT, because EdepSim writes to ROOT by default. So we load it.
import ROOT as rt
rt.gStyle.SetOptStat(0)
# load our library that produces a LArTPC-like image using EDepSim
from simpledet import simpledet
# load schema definition
import simpledet.petastorm.petastorm_schema as schema

# load the class that executes the conversion
IEdepSim = simpledet.edepsim.EDepSimInterface()
print(IEdepSim)

# input file: output of EDepSim
if not os.path.exists(args.input_edepsim):
    print("Cannot find input EDepSim file at ",args.input_edepsim)
    print("Quitting")
    sys.exit(1)

inputfile = rt.TFile( args.input_edepsim, "open" )
edeptree = inputfile.Get("EDepSimEvents")
if edeptree is None:
    print("Cannot load the expected EDepSimEvents ROOT tree in the input file. Qutting.")
    sys.exit(1)
nentries = edeptree.GetEntries()
print("Loaded EDepSimEvents tree. Number of entries: ",nentries)

# we collect data for each entry, i.e. simulated image
c1 = rt.TCanvas("c1","",1600,600)
c1.Divide(2,1)
entry_data = []
for ientry in range(nentries):

    edeptree.GetEntry(ientry)

    seghit_v = edeptree.Event.SegmentDetectors["drift"]
    print("number of seghits: ",seghit_v.size())
    
    cropped_image = IEdepSim.makeNumpyArrayCrop( seghit_v, cropsize, -64, 0, 0 )
    print("cropped_image.shape=",cropped_image.shape)
    himage = IEdepSim.makeWholeDetectorTH2D( seghit_v )
    c1.cd(1)
    c1.cd(1).SetGridx(1)
    c1.cd(1).SetGridy(1)    
    himage.Draw("colz")

    #hcrop = rt.TH2D("hcrop","",cropsize,-0.5*cropsize*0.3,0.5*cropsize*0.3,cropsize,-0.5*cropsize*0.3,0.5*cropsize*0.3)
    hcrop = rt.TH2D("hcrop","",cropsize,0,cropsize,cropsize,0,cropsize)
    for i in range(cropsize):
        for j in range(cropsize):
            hcrop.SetBinContent(i+1,j+1,cropped_image[i,j])
    c1.cd(2)
    c1.cd(2).SetGridx(1)
    c1.cd(2).SetGridy(1)        
    hcrop.Draw("colz")
    c1.Update()
    print("[ENTER] to continue")
    input()
    break






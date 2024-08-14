import os,sys
import argparse,signal

parser = argparse.ArgumentParser(
    prog='run_edepsim2hdf5.py',
    description='Example/Test saving simpledet image into petastorm DB.',
    epilog='Text at the bottom of help')

parser.add_argument('--input-edepsim', '-i', required=True, type=str,
                    help='path to input ROOT edepsim file')
parser.add_argument('--out-hdf5', '-o', required=True, type=str,
                    help='Name of HDF5 file')
parser.add_argument('--start-index', '-s', required=True, type=int,
                    help='We want each entry to have a unique index: this sets the starting index to use.')
parser.add_argument('--class-index', '-c', required=True, type=int,
                    help='The class index for the type of image we are processing.')
parser.add_argument('-ow',"--over-write",default=False,action='store_true',
                    help="If flag given, will overwrite existing output file. Otherwise, will quit.")


# Set arguments and other parameters
cropsize = 256
args = parser.parse_args()

import numpy as np
import h5py

# we need ROOT, because EdepSim writes to ROOT by default. So we load it.
import ROOT as rt
rt.gStyle.SetOptStat(0)
# load our library that produces a LArTPC-like image using EDepSim
from simpledet import simpledet
# load schema definition
import simpledet.petastorm.petastorm_schema as schematools

# load the class that executes the conversion from EDepSim file to images and label
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

# print("///////////////////////////////////////////////////////////////////")
# print(" TRAINING DATA SAVED TO DB WILL HAVE THE FOLLOWING PARTITION LABEL")
# print(partition_label)
# print("------------------------")
# print("Schema")
# print(schema)
# print("------------------------")
# print("DB folder: ",output_url)
# print("-----------------------------------")
# print("This script will create the folder:")
# print(chunk_folder)
# print("Exists: ",os.path.exists(chunk_folder))
# print("///////////////////////////////////////////////////////////////////")

# =========================================================
# Dictionary that defines the column in the data table
# Class Index definitions
class_indices_dict = {"electron":0,
                      "photon":1,
                      "darknu":2 }

columns = {"entryindex":[], # integer, labeling the entry
            "img":[],     # image whose pixel values represent ionization energy 
            "segment":[], # image whose pixel values represent trackid
            "classindex":[],   # class index, see class_indices_dict
            "Evis":[],    # visible energy: simply the pixel sum for now (no conversion)
            "truthNparticles":[], # number of particles whose information we have saved from geant4
            "pdg":[],        # list of pdg codes as int numpy array. note: the array is padded to a max of 50 particles
            "motherindex":[] # (index+1) of mother particle in pdg (and motherindex) array. Use to assemble particle graph
}


class EntryData:
    def __init__(self):
        self.entryindex = -1
        self.img     = np.zeros((64,64),dtype=np.float32)
        self.segment = np.zeros((64,64),dtype=np.float32)
        self.timeorder = np.zeros((64,64),dtype=np.float32)
        self.class_index = -1
        self.Evis = 0.0
        self.truthNparticles = 0
        self.pdg = np.zeros( 50, dtype=np.int64 )
        self.motherindex = np.zeros( 50, dtype=np.int32 )

if os.path.exists(args.out_hdf5):
    # remove past partition from database if found        
    print("*****  output file exists: ",args.out_hdf5,"  **********")
    if args.over_write:
        print("removing without check due to '--over-write' flag provided")
        os.system("rm -r %s"%(args.out_hdf5))
    else:
        print("overwrite not allowed. Quitting.")
        sys.exit(1)

# we collect data for each entry, i.e. simulated image
data = []
trackid_to_index = {}
for ientry in range(nentries):

    edeptree.GetEntry(ientry)
    print("=========================================")
    print("[ENTRY ",ientry,"]")
          
    # get struct with variables we will fill:
    entry_data = EntryData()
    entry_data.entryindex = args.start_index + ientry
    print("entryindex=",entry_data.entryindex)

    # Get Primary Information
    prim_v = edeptree.Event.Primaries
    print("number of primary vertices: ",prim_v.size())
    nparticles = 0
    for ivertex in range(prim_v.size()):
        #print("VERTEX[",ivertex,"]")
        vertex = prim_v.at(ivertex)

        for iprim in range(vertex.Particles.size()):
            primpart = vertex.Particles.at(iprim)
            if nparticles<50:
                entry_data.pdg[nparticles] = primpart.GetPDGCode()
                trackid_to_index[primpart.GetTrackId()] = nparticles
                # set mother id here (later)
            nparticles += 1

    
    # Get Location of Energy deposits from EDepSim
    seghit_v = edeptree.Event.SegmentDetectors["drift"]
    print("number of seghits: ",seghit_v.size())

    # process the edep sim information and make the 2D projection readout plane image
    # this uses the simpledet library
    isgood = IEdepSim.processSegmentHits( seghit_v )
    
    # turn the processed information into various images, i.e. array with labels
    """
    PyObject* makeNumpyArrayCrop( const TG4HitSegmentContainer& hit_container, int img_pixdim,
				  int offset_x_pixels, int offset_y_pixels, int rand_pix_from_center );
    """
    threshold = 0.005
    cropped_dict = IEdepSim.makeNumpyArrayCrop( seghit_v, cropsize, -64, 0, threshold, 0 )
    cropped_image = cropped_dict["edep"]
    print("cropped_image.shape=",cropped_image.shape)

    # give the images to our entry_data struct
    entry_data.img = cropped_dict["edep"]
    entry_data.segment = cropped_dict['trackid']
    entry_data.timeorder = cropped_dict['timestepmask']
    entry_data.Evis = entry_data.img.sum()
    entry_data.class_index = args.class_index
    entry_data.truthNparticles = nparticles

    # append to data container
    data.append( entry_data )

    # # set conditional to true to visualize entry
    # if args.visualize:
    #     c1 = rt.TCanvas("c1","",1600,1200)
    #     c1.Divide(1,2)
    #     himage = IEdepSim.makeWholeDetectorTH2D( seghit_v )
    #     c1.cd(1)
    #     c1.cd(1).SetGridx(1)
    #     c1.cd(1).SetGridy(1)    
    #     himage.Draw("colz")

    #     c1.cd(2).Divide(4,1)

    #     #hcrop = rt.TH2D("hcrop","",cropsize,-0.5*cropsize*0.3,0.5*cropsize*0.3,cropsize,-0.5*cropsize*0.3,0.5*cropsize*0.3)
    #     hcrop        = rt.TH2D("hcrop","Deposited Energy",cropsize,0,cropsize,cropsize,0,cropsize)
    #     hcrop_tid    = rt.TH2D("hcrop_tid","Track IDs",cropsize,0,cropsize,cropsize,0,cropsize)
    #     hcrop_tsteps = rt.TH2D("hcrop_tsteps","Time step indices",cropsize,0,cropsize,cropsize,0,cropsize)        
    #     hedep        = rt.TH1D("hedep","Pixel Edep; MeV;num pixels",50,0,1.0)
    #     for i in range(cropsize):
    #         for j in range(cropsize):
    #             if cropped_image[i,j]>0.1*threshold:
    #                 hcrop.SetBinContent(i+1,j+1,cropped_image[i,j])
    #                 hcrop_tid.SetBinContent(i+1,j+1,cropped_dict['trackid'][i,j])
    #                 hcrop_tsteps.SetBinContent(i+1,j+1,cropped_dict['timestepmask'][i,j])
    #                 hedep.Fill( cropped_image[i,j] )
    #     c1.cd(2).cd(1)
    #     c1.cd(2).cd(1).SetGridx(1)
    #     c1.cd(2).cd(1).SetGridy(1)        
    #     hcrop.Draw("colz")
    #     c1.cd(2).cd(2)
    #     c1.cd(2).cd(2).SetGridx(1)
    #     c1.cd(2).cd(2).SetGridy(1)        
    #     hcrop_tid.Draw("colz")
    #     c1.cd(2).cd(3)
    #     hcrop_tsteps.Draw("colz")
    #     c1.cd(2).cd(4)
    #     hedep.Draw("hist")        
    #     c1.Update()
    #     print("[ENTER] to continue")
    #     input()


# Write to HDF5
with h5py.File(args.out_hdf5, 'w') as hf:
    for entry_data in data:
        # We store each image as its own data set
        # This creates easy random order access over multiple files
        # But this will be slow, because we won't chunk read.
        i = entry_data.entryindex
        hf.create_dataset(f'class_{i}', data=entry_data.class_index )
        hf.create_dataset(f'evis_{i}',  data=entry_data.Evis )
        hf.create_dataset(f'nparticles_{i}', data=entry_data.truthNparticles )
        hf.create_dataset(f'img_{i}',   data=entry_data.img, compression='gzip', compression_opts=9)
        hf.create_dataset(f'pdg_{i}',   data=entry_data.pdg, compression='gzip', compression_opts=9)
        

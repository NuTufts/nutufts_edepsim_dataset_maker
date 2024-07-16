import os,sys
import argparse,signal
import numpy as np
from pyspark.sql import SparkSession
from petastorm.etl.dataset_metadata import materialize_dataset
from petastorm.unischema import dict_to_spark_row

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
parser.add_argument('--pdgcode', '-pdg', required=True, type=int,
                    help='Indicate the particle type being saved')
parser.add_argument('--runid','-r',required=True,type=int,
                    help='Label to index partitions of this type')
parser.add_argument("--do-not-write-to-db","-g",required=False,action='store_true',default=False,
                    help='if flag provided, run in debug mode and do not write to the database')
parser.add_argument('--port',required=False,type=int,default=4000,
                    help='Set the starting port number for the spark web UI')
parser.add_argument('-ow',"--over-write",default=False,action='store_true',
                    help="If flag given, will overwrite existing database chunk without user check")

cropsize = 256

args = parser.parse_args()

# we need ROOT, because EdepSim writes to ROOT by default. So we load it.
import ROOT as rt
rt.gStyle.SetOptStat(0)
# load our library that produces a LArTPC-like image using EDepSim
from simpledet import simpledet
# load schema definition
import simpledet.petastorm.petastorm_schema as schematools

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

partition_label = "pdg%d_run%04d_%s"%(args.pdgcode, args.runid, args.tag)
schema = schematools.get_schema("v0")
output_url="file:///"+args.petastorm_db_folder
chunk_folder = args.petastorm_db_folder+"/partition=%s"%(partition_label)
print("///////////////////////////////////////////////////////////////////")
print(" TRAINING DATA SAVED TO DB WILL HAVE THE FOLLOWING PARTITION LABEL")
print(partition_label)
print("------------------------")
print("Schema")
print(schema)
print("------------------------")
print("DB folder: ",output_url)
print("-----------------------------------")
print("This script will create the folder:")
print(chunk_folder)
print("Exists: ",os.path.exists(chunk_folder))
print("///////////////////////////////////////////////////////////////////")

if os.path.exists(chunk_folder):
    # remove past partition from database if found        
    print("*****  removing old database chunk folder: ",chunk_folder,"  **********")
    if args.over_write:
        print("proceeding without check due to '--over-write' flag has been given")
        os.system("rm -r %s"%(chunk_folder))
    else:
        print("overwrite not allowed of folder: ",chunk_folder)
        sys.exit(1)

# we collect data for each entry, i.e. simulated image
data = []
for ientry in range(nentries):

    edeptree.GetEntry(ientry)
    print("=========================================")
    print("[ENTRY ",ientry,"]")
          

    # Get Primary Information
    prim_v = edeptree.Event.Primaries
    print("number of primary vertices: ",prim_v.size())
    prim_mom4_v = []
    prim_pos4_v = []
    prim_pdg_v = []
    for ivertex in range(prim_v.size()):
        print("VERTEX[",ivertex,"]")
        vertex = prim_v.at(ivertex)
        prim_pos = np.zeros(4,dtype=np.float32)
        for v in range(3):
            prim_pos[v] = vertex.GetPosition()[v]*0.1 # mm to cm
        prim_pos[3] = vertex.GetPosition()[3]
        print("  pos4=",prim_pos)
        prim_pos4_v.append( prim_pos )
        
        mom4_v = []
        pdgcode_v = []
        for iprim in range(vertex.Particles.size()):
            primpart = vertex.Particles.at(iprim)
            prim_mom = np.zeros(4,dtype=np.float32)
            for v in range(4):
                prim_mom[v] = primpart.GetMomentum()[v]
            print("  primary[",iprim,"] ",primpart.GetName()," pdg=",primpart.GetPDGCode()," trackid=",primpart.GetTrackId())
            print("    mom4=",prim_mom)
            pdgcode_v.append( primpart.GetPDGCode() )
            mom4_v.append(prim_mom)
        prim_mom4_v.append( mom4_v )
        prim_pdg_v.append( pdgcode_v )
        

    
    # Get Trajectory information
    traj_v = edeptree.Event.Trajectories
    print("Number of trajectories: ",traj_v.size())
    #for itraj in range(traj_v.size()):
    #    traj = traj_v.at(itraj)
    #    print("Trajectory[",itraj,"] trackid=",traj.GetTrackId()," nsteps=",traj.Points.size())
    first_trajpoint_pos4 = traj_v.at(0).Points.at(0).GetPosition()
    first_edep = np.zeros(4,dtype=np.float32)
    for v in range(3):
        first_edep[v] = first_trajpoint_pos4[v]*0.1 # mm to cm
    first_edep[3] = first_trajpoint_pos4[3]

    # Get Location of Energy deposits and turn into an image
    seghit_v = edeptree.Event.SegmentDetectors["drift"]
    print("number of seghits: ",seghit_v.size())

    # some meta data?
    first_seghit = seghit_v.at(0)

    depth = IEdepSim.distance_to_readout_plane # default is 128.0 cm, in the future we can vary this
    """
    PyObject* makeNumpyArrayCrop( const TG4HitSegmentContainer& hit_container, int img_pixdim,
				  int offset_x_pixels, int offset_y_pixels, int rand_pix_from_center );
    """
    threshold = 0.005
    cropped_dict = IEdepSim.makeNumpyArrayCrop( seghit_v, cropsize, -64, 0, threshold, 0 )
    cropped_image = cropped_dict["edep"]
    print("cropped_image.shape=",cropped_image.shape)

    # variables to figure out
    mom4 = np.zeros(4,dtype=np.float32)
    mom4 = prim_mom4_v[0][0]
    pre_edep_len = np.power( prim_pos4_v[0][:3]-first_edep[:3], 2 ).sum()
    print("pre_edep_len: ",pre_edep_len)
    dedx_20pix = np.zeros(20,dtype=np.float32)

    entry_data = {"partition":partition_label,
                  "runid":args.runid,
                  "entry":ientry,
                  "pdgcode":prim_pdg_v[0][0],
                  "depth":depth,
                  "momentum4":mom4,
                  "preedeplen":pre_edep_len,
                  "dedx_20pix":dedx_20pix,
                  "edepimage":cropped_image}

    # append to data container
    data.append( dict_to_spark_row(schema,entry_data) )

    # set conditional to true to visualize entry
    if False:
        c1 = rt.TCanvas("c1","",1600,1200)
        c1.Divide(1,2)
        himage = IEdepSim.makeWholeDetectorTH2D( seghit_v )
        c1.cd(1)
        c1.cd(1).SetGridx(1)
        c1.cd(1).SetGridy(1)    
        himage.Draw("colz")

        c1.cd(2).Divide(3,1)

        #hcrop = rt.TH2D("hcrop","",cropsize,-0.5*cropsize*0.3,0.5*cropsize*0.3,cropsize,-0.5*cropsize*0.3,0.5*cropsize*0.3)
        hcrop     = rt.TH2D("hcrop","",cropsize,0,cropsize,cropsize,0,cropsize)
        hcrop_tid = rt.TH2D("hcrop_tid","",cropsize,0,cropsize,cropsize,0,cropsize)
        hedep     = rt.TH1D("hedep","",50,0,1.0)
        for i in range(cropsize):
            for j in range(cropsize):
                hcrop.SetBinContent(i+1,j+1,cropped_image[i,j])
                hcrop_tid.SetBinContent(i+1,j+1,cropped_dict['trackid'][i,j])
                if cropped_image[i,j]>0.1*threshold:
                    hedep.Fill( cropped_image[i,j] )
        c1.cd(2).cd(1)
        c1.cd(2).cd(1).SetGridx(1)
        c1.cd(2).cd(1).SetGridy(1)        
        hcrop.Draw("colz")
        c1.cd(2).cd(2)
        c1.cd(2).cd(2).SetGridx(1)
        c1.cd(2).cd(2).SetGridy(1)        
        hcrop_tid.Draw("colz")
        c1.cd(2).cd(3)
        hedep.Draw("hist")
        c1.Update()
        print("[ENTER] to continue")
        input()
        break


if not args.do_not_write_to_db:
    print("********** WRITING TO SPARK DB ***************")
    spark_session = SparkSession.builder.config('spark.driver.memory', '2g').master('local[2]').config("spark.ui.port", "%d"%(args.port)).getOrCreate()
    sc = spark_session.sparkContext
    
    # save data to file
    print("writing ",len(data)," entries into the database")
    rowgroup_size_mb=256
    write_mode='overwrite'
    with materialize_dataset(spark_session, output_url, schema, rowgroup_size_mb):
        print("store rows to parquet file")
        spark_session.createDataFrame( data, schema.as_spark_schema() ) \
                     .coalesce( 1 ) \
                     .write \
                     .partitionBy('partition') \
                     .mode(write_mode) \
                     .parquet( output_url )
        print("spark write operation")
else:
    print("DEBUG MODE: skip data base writing")
    print("Number of entries prepared: ",len(data))
    



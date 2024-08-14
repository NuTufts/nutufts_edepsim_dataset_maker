import os,sys,time
import argparse


parser = argparse.ArgumentParser(
    prog='test_hdf5_dataloder.py',
    description='Example of setting up a data loader',
    epilog='Text at the bottom of help')

parser.add_argument('--input', '-i', required=True, type=str,
                    help='path to hdf-file or folder')
parser.add_argument('--niterations', '-n', required=False, type=int, default=5,
                    help='number of iterations')
parser.add_argument("--visualize", '-v', required=False, default=False,action='store_true',
                    help='if flag provided, will draw images in the batch')
parser.add_argument("--batchsize", '-b', required=False, default=4, type=int,
                    help="Batch size per iteration")

args = parser.parse_args()

import h5py
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from hdf5dataset import HDF5Dataset, get_data_loader
if args.visualize:
    import ROOT as rt
    rt.gStyle.SetOptStat(0)


finput_v = []
if os.path.isdir( args.input ):
    flist = os.listdir( args.input )
    for f in flist:
        finput_v.append( args.input + "/" + f.strip() )
else:
    # single file
    finput_v = [args.input]

batch_size = args.batchsize
hdf5_filelist = finput_v
train_loader = get_data_loader(hdf5_filelist, batch_size=batch_size)
print("Number of entries in the data loader: ", len(train_loader))

if args.visualize:
    max_col = 4
    if batch_size<3:
        nrows = 1
    else:
        nrows = int(batch_size/3)
    
    ncols = max_col
    if nrows<1:
        if batch_size<max_col:
            ncols = batch_size
            
    c = rt.TCanvas("c","batch images",500*ncols, nrows*400)
    c.Divide( ncols, nrows )
    c.Draw()

iiter = 0
while iiter<args.niterations:
    for batch_idx, (images, labels) in enumerate(train_loader):
        print("--------------------------------------")
        print("iteration[",iiter,"] batchidx[",batch_idx,"]")
        print(images.shape)
        hbatch_v = []
        for ib in range(images.shape[0]):
            print("[",ib,"] sum=",images[ib,:,:].sum()," img>0.05=",(images[ib,:,:]>0.05).sum())

            if args.visualize:
                imgshape = images[ib].shape
                c.cd(ib+1)
                h = rt.TH2D( "h%d"%(ib),"batch[%d] classindex=%d"%(ib,labels[ib]), imgshape[0], 0, imgshape[0], imgshape[1], 0, imgshape[1] )
                for ix in range(imgshape[0]):
                    for iy in range(imgshape[1]):
                        h.SetBinContent( ix+1, iy+1, images[ib,ix,iy] )
                h.SetMaximum(2.0)
                h.Draw("colz")
                hbatch_v.append(h)
        if args.visualize:
            c.Update()
            print("[entry] to continue")
            input()
            for h in hbatch_v:
                del h

        iiter += 1
        if iiter>=args.niterations:
            break


print("closing ... (pause to allow dataloader threads to finish)")
time.sleep(1)
print("fin")

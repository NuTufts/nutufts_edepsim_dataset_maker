import os,sys,time
import argparse

import simpledet
from simpledet.petastorm.reader import get_dataloader

parser = argparse.ArgumentParser(
    prog='test_dataloder.py',
    description='Example of setting up a data loader',
    epilog='Text at the bottom of help')

parser.add_argument('--petastorm-db-folder', '-db', required=True, type=str,
                    help='path to petastorm database folder')
parser.add_argument('--niterations', '-n', required=False, type=int, default=5,
                    help='number of iterations')
parser.add_argument("--visualize", '-v', required=False, default=False,action='store_true',
                    help='if flag provided, will draw images in the batch')

args = parser.parse_args()

import ROOT as rt
rt.gStyle.SetOptStat(0)

database_url = "file://"+args.petastorm_db_folder

batchsize = 4
dataloader = get_dataloader( database_url, 'v0', batchsize, shuffle_rows=True )

data_iter = iter(dataloader)

if args.visualize:
    nrows = int(batchsize/5)
    ncols = 5
    if nrows<1:
        if batchsize<5:
            ncols = batchsize
            
    c = rt.TCanvas("c","batch images",500*batchsize, (nrows+1)*600)
    c.Divide( batchsize, nrows+1 )
    c.Draw()

for iteration in range(args.niterations):

    print("--------------------------------------")
    print("iteration[",iteration,"]")
    batch = next(data_iter)
    print("  image batch: ",batch['edepimage'].shape)
    print("  class index: ",batch['classindex'])
    print("  entry index: ",batch['entryindex'])

    if args.visualize:
        imgshape = batch['edepimage'].shape
        hbatch_v = []
        for b in range(batchsize):
            c.cd(b+1)
            h = rt.TH2D( "h%d"%(b),"batch[%d] entry[%d][%d]"%(b,batch['entryindex'][b,0],batch['entryindex'][b,1]), imgshape[1], 0, imgshape[1], imgshape[2], 0, imgshape[2] )
            for ix in range(imgshape[1]):
                for iy in range(imgshape[2]):
                    h.SetBinContent( ix+1, iy+1, batch['edepimage'][b,ix,iy] )
            h.Draw("colz")
            hbatch_v.append(h)
        c.Update()
        print("[entry] to continue")
        input()
        for h in hbatch_v:
            del h

print("closing ... (pause to allow dataloader threads to finish)")
time.sleep(1)
print("fin")

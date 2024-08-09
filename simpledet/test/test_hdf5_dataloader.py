import os,sys,time
import argparse


parser = argparse.ArgumentParser(
    prog='test_hdf5_dataloder.py',
    description='Example of setting up a data loader',
    epilog='Text at the bottom of help')

parser.add_argument('--input', '-i', required=True, type=str,
                    help='path to hdf-file')
parser.add_argument('--niterations', '-n', required=False, type=int, default=5,
                    help='number of iterations')
parser.add_argument("--visualize", '-v', required=False, default=False,action='store_true',
                    help='if flag provided, will draw images in the batch')

args = parser.parse_args()

import h5py
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import ROOT as rt

# Example of defining a data loader class
class HDF5Dataset(Dataset):
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.dataset_lengths = []
        self.cumulative_lengths = [0]
        # we have to scan the files to map out which file has which indices
        for file_path in file_paths:
            with h5py.File(file_path, 'r') as hf:
                length = len(hf.keys()) // 5  # Divide by number of columns in each entry
                self.dataset_lengths.append(length)
                self.cumulative_lengths.append(self.cumulative_lengths[-1] + length)
        
    def __len__(self):
        return self.cumulative_lengths[-1]
    
    def __getitem__(self, idx):
        file_idx = np.searchsorted(self.cumulative_lengths, idx, side='right') - 1
        local_idx = idx - self.cumulative_lengths[file_idx]
        
        with h5py.File(self.file_paths[file_idx], 'r') as hf:
            img = np.array(hf[f'img_{local_idx}'])
            class_idx = np.array(hf[f'class_{local_idx}'])
        
        # Convert to torch tensor and normalize if needed
        img_tensor = torch.from_numpy(img).float()
        
        return img_tensor, torch.tensor(class_idx, dtype=torch.long)

# Usage example
def get_data_loader(file_paths, batch_size=2, num_workers=1):
    dataset = HDF5Dataset(file_paths)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)


hdf5_filelist = [args.input]
train_loader = get_data_loader(hdf5_filelist)
print("Number of entries in the data loader: ", len(train_loader))

if args.visualize:
    nrows = int(batchsize/5)
    ncols = 5
    if nrows<1:
        if batchsize<5:
            ncols = batchsize
            
    c = rt.TCanvas("c","batch images",500*batchsize, (nrows+1)*600)
    c.Divide( batchsize, nrows+1 )
    c.Draw()

iiter = 0
while iiter<args.niterations:
    for batch_idx, (images, labels) in enumerate(train_loader):
        print("--------------------------------------")
        print("iteration[",iiter,"] batchidx[",batch_idx,"]")
        print(images.shape)
        for ib in range(images.shape[0]):
            print("[",ib,"] sum=",images[ib,:,:].sum()," img>0.05=",(images[ib,:,:]>0.05).sum())
        print("labels: ",labels)
        iiter += 1
        if iiter>=args.niterations:
            break

    # if args.visualize:
    #     imgshape = batch['edepimage'].shape
    #     hbatch_v = []
    #     for b in range(batchsize):
    #         c.cd(b+1)
    #         h = rt.TH2D( "h%d"%(b),"batch[%d] entry[%d][%d]"%(b,batch['entryindex'][b,0],batch['entryindex'][b,1]), imgshape[1], 0, imgshape[1], imgshape[2], 0, imgshape[2] )
    #         for ix in range(imgshape[1]):
    #             for iy in range(imgshape[2]):
    #                 h.SetBinContent( ix+1, iy+1, batch['edepimage'][b,ix,iy] )
    #         h.Draw("colz")
    #         hbatch_v.append(h)
    #     c.Update()
    #     print("[entry] to continue")
    #     input()
    #     for h in hbatch_v:
    #         del h

print("closing ... (pause to allow dataloader threads to finish)")
time.sleep(1)
print("fin")

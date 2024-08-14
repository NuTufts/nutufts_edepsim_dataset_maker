import os,sys

import h5py
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

# Example of defining a data loader class
class HDF5Dataset(Dataset):
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.dataset_lengths = []
        self.cumulative_lengths = [0]
        # we have to scan the files to map out which file has which indices
        for file_path in file_paths:
            with h5py.File(file_path, 'r') as hf:
                nkeys = len(hf.keys())
                length = nkeys // 5  # Divide by number of columns in each entry
                print("length=",nkeys," for ",file_path)
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


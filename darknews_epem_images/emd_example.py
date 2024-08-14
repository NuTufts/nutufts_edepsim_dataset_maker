import os,sys
import numpy as np
import geomloss
import torch

"""
Example of how to calculate the EMD between two images.

We are using the geoloss package: https://www.kernel-operations.io/geomloss/

Requires additional packages:

pip3 install --user pykeops
pip3 install --user geomloss
"""

from hdf5dataset import get_data_loader

electron_dataset = "data/devsample_electron_100mev.hdf5"
gamma_dataset = "data/devsample_gamma_100mev.hdf5"

electron_loader = get_data_loader( [electron_dataset], batch_size=1, num_workers=1 )
gamma_loader    = get_data_loader( [gamma_dataset], batch_size=1, num_workers=1 )

electron_iter = iter(electron_loader)
gamma_iter    = iter(gamma_loader)

electron_example = next(electron_iter)[0]
gamma_example    = next(gamma_iter)[0]
#gamma_example    = next(electron_iter)[0] # seeing what would happen

print(electron_example.shape)

# Use what's called the Sinkhorn Divergence to calculate an approximate Earth Mover's distance
sinkhorn_fn = geomloss.SamplesLoss(loss='sinkhorn', p=1, blur=0.05)

# we have to normalize the pictures, so that they are probability distribution functions
# all values must be greater than zero, and the sum of all the pixels must add to 1.0

# make positive, by selecting pixels < 0.0 and setting them to 0.0
electron_example[ electron_example<0.0 ] = 0.0
gamma_example[ gamma_example<0.0 ] = 0.0

# convert images as a list of pixels as well, first unrolling
electron_pix_list = electron_example.reshape( (256*256,1) )
gamma_pix_list    = gamma_example.reshape( (256*256,1) )
electron_nonzero_indices = (electron_pix_list>0.05).squeeze()
gamma_nonzero_indices    = (gamma_pix_list>0.05).squeeze()
print("electron_nonzero_indices.shape: ",electron_nonzero_indices.shape)
print("electron_nonzero_indices.sum: ",electron_nonzero_indices.sum())


# define the coordinate grid
# each entry in array has (i,j) position
image_grid = np.zeros( electron_example.shape )
x = np.arange(256)
y = np.arange(256)
xx, yy = np.meshgrid(x, y)
coords = np.stack((yy, xx), axis=-1).astype(np.float64)
print("coords: ",coords.shape)

for i in range(10):
    # spot check of grid
    x_i = np.random.randint(0,256)
    y_i = np.random.randint(0,256)
    print( "spot check: ",(x_i,y_i),": ",coords[x_i,y_i] )

# normalize coordinate grid between (0.,1.)
coords /= 256.0
# norm reshape coord grid into a list
coord_list = torch.from_numpy( coords.reshape( (256*256,2) ) )
print("coord_list: ",coord_list.shape)
print(coord_list)

# now select pixel values and coordinates for each image
electron_pixvalues = electron_pix_list[ electron_nonzero_indices[:] ]
electron_coords    = coord_list[ electron_nonzero_indices[:], :]
gamma_pixvalues    = gamma_pix_list[ gamma_nonzero_indices[:] ]
gamma_coords       = coord_list[ gamma_nonzero_indices[:], :]

# normalize pixvalues
e_sum = electron_pixvalues.sum()
g_sum = gamma_pixvalues.sum()
electron_pixvalues /= e_sum
gamma_pixvalues /= g_sum

# turn into torch tensors?
#electron_pix_list = torch.from_numpy( electron_pix_list)
#gamma_pix_list    = torch.from_numpy( gamma_pix_list )

print("electron pdf: ",electron_pixvalues.shape)
print("electron coords: ",electron_coords.shape)

print("gamma pdf: ",gamma_pixvalues.shape)
print("gamma coord: ",gamma_coords.shape)

emd = sinkhorn_fn( electron_pixvalues, electron_coords, gamma_pixvalues, gamma_coords )
print("Earth Mover's Distance: ",emd)
print("sum(electron): ",e_sum)
print("sum(gamma): ",g_sum)
print("(sum(electron)-sum(gamma))/mean_total: ",(e_sum-g_sum)/(0.5*(e_sum+g_sum)))

#emd_ee = sinkhorn_fn( electron_pixvalues, electron_coords, electron_pixvalues, electron_coords )
#print("Earth Mover's Distance (e vs. e sanity check, should be zero: ",emd_ee)

# TO DO: Visualize the examples
# Also, can I visualize the transport plan?

import os,sys
import numpy as np

from petastorm import make_reader, TransformSpec
from petastorm.pytorch import DataLoader
from petastorm.codecs import NdarrayCodec
import torch

def _default_classifier_row( row ):
    #print(row)
    img = row['edepimage']
    pdgcode = row['pdgcode']
    if abs(pdgcode)==22:
        classindex = np.array((0,),dtype=np.int64)
    elif abs(pdgcode)==11:
        classindex = np.array((1,),dtype=np.int64)
    else:
        raise ValueError("PDG code unexpected, no class index for pdgcode=",pdgcode)

    result = { "edepimage":img,
               "classindex":classindex,
               "entryindex":np.array( (row['runid'],row['entry']), dtype=np.int64 ) }
    
    return result

def simpledet_collate_fn_v0( batchdata ):
    #print("collate_fn")
    #print(batchdata)
    batchsize = len(batchdata)
    batchout = {"edepimage":torch.from_numpy( np.concatenate( [ np.expand_dims(x['edepimage'],0) for x in batchdata ], axis=0 ) ),
                "classindex":torch.from_numpy( np.concatenate( [ np.expand_dims(x['classindex'],0) for x in batchdata ], axis=0 ) ),
                "entryindex":torch.from_numpy( np.concatenate( [ np.expand_dims(x['entryindex'],0) for x in batchdata ], axis=0 ) ) }

    return batchout

def get_dataloader( dataset_folder, version, batch_size, num_epochs=None, shuffle_rows=False, seed=314159 ):
    if version=="v0":
        classifier_transform = TransformSpec( _default_classifier_row,
                                              removed_fields=['partition','runid','entry','depth','momentum4','preedeplen','dedx_20pix','pdgcode'],
                                              edit_fields=[('classindex',np.int64,(None,1),NdarrayCodec(),False),
                                                           ('entryindex',np.int64,(None,2),NdarrayCodec(),False)])
        
        loader = DataLoader( make_reader( dataset_folder, num_epochs=num_epochs,
                                          transform_spec=classifier_transform,
                                          seed=seed,
                                          workers_count=1,
                                          shuffle_rows=shuffle_rows,
                                         ),
                             batch_size=batch_size,
                             collate_fn=simpledet_collate_fn_v0 )
        return loader

    raise ValueError("data loader version not recognized: ",version)
                                          
    

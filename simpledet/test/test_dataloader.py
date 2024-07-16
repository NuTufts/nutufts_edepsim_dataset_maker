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

args = parser.parse_args()

database_url = "file://"+args.petastorm_db_folder

dataloader = get_dataloader( database_url, 'v0', 4, shuffle_rows=True )

data_iter = iter(dataloader)

for iteration in range(args.niterations):

    print("--------------------------------------")
    print("iteration[",iteration,"]")
    batch = next(data_iter)
    print("  image batch: ",batch['edepimage'].shape)
    print("  class index: ",batch['classindex'])
    print("  entry index: ",batch['entryindex'])
    

print("closing ... (pause to allow dataloader threads to finish)")
time.sleep(1)
print("fin")

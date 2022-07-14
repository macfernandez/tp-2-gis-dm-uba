import pandas as pd
import rasterio as rio
import subprocess
from typing import *
import glob
import os

def calc_n_pix(input_folder):
    crops = {}
    results = glob.glob(input_folder + '*.tif')
    for file in results:
    print('Calculando ' + file)
    filename = os.path.splitext(os.path.basename(file))[0]
    raster = rio.open(file).read()
    raster_crop = raster[raster==1]
    sum_pixels = raster_crop.sum()
    print(sum_pixels)
    crops[filename] = [sum_pixels]
    
    df_pixeles = pd.DataFrame(crops).T

    print(df_pixeles)

if __name__ == '__main__':

    import argparse

    all_index = list(indexes.keys())

    parser = argparse.ArgumentParser(
        prog='Calculadora de número total de pixeles en el tile',
        description='Calcula el numero total de pixeles en una lista de tiles, parte final de bitácora'
    )
    parser.add_argument('input_folder', type=str, help='Folder with .tif files for using as input.')
    args = parser.parse_args()

    if not args.index:
        args.__setattr__('index',all_index)

    for i in args.index:
        calc_n_pix(
            input_folder=args.input_folder,
        )
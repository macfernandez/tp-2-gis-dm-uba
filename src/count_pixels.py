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
    df_pixeles.rename(columns={ df_pixeles.columns[0]: "Pixeles" }, inplace = True)
    df_pixeles['Hectareas'] = df_pixeles['Pixeles'] * 0.04
    return print(df_pixeles)

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        prog='Calculadora de número total de pixeles en el tile',
        description='Calcula el numero total de pixeles en una lista de tiles, parte final de bitácora'
    )
    parser.add_argument('input_folder', type=str, help='Folder with .tif files for using as input.')
    args = parser.parse_args()
    
    calc_n_pix(input_folder=args.input_folder)
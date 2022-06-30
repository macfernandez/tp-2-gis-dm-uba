import os
import subprocess
from typing import *
from glob import glob

from src.utils import save_file_in_bucket
from src.indexes_definition import indexes


def concatenate(input_folder:str, tile:str, index:str, output_folder:str, bucket:Union[str,None]=None)->None:
    '''
        Concatenate .tif files in input_folder's subfolders.
        Filter by tile and index and save the result in output_folder.
        If bucket, save output file in bucket and output_folder works as tmp
        location.

        Parameters
        ----------
            input_folder: str
                Folder with subfolders and .tif files.

            tile: str
                Image's tile.

            index: str
                Spectral index.

            output_folder: str
                Output folder.

            bucket: str, default: None
                GCP Bucket location URI for output file.
                If None, output file is not saved in bucket.

        Returns
        -------
            None

    '''
    images = sorted(glob(f'{input_folder}/*/*{tile}_{index.lower()}.tif'))
    images_otb = ' '.join(images)
    im_out_fname = f'{output_folder}/{tile}_{index.lower()}.tif'
    cmd = """bash -c 'source ~/OTB-8.0.1-Linux64/otbenv.profile;\
        otbcli_ConcatenateImages -il {im} -out {im_out} -ram {memoria}'""".format(
            im=images_otb, im_out=im_out_fname
    )
    subprocess.run(cmd, shell=True)
    if bucket:
            save_file_in_bucket(im_out_fname, bucket)
            os.remove(im_out_fname)
    print(f'\n***** {index} concatenated.\n')


if __name__ == '__main__':
    
    import argparse

    all_index = list(indexes.keys())

    parser = argparse.ArgumentParser(
        prog='Calculador de índices espectrales',
        description='Calcula los índices espectrales NDVI, NDVI_a, NDSI, NBI, NDWI (Gao) y DNWI (McFeeters).'
    )
    parser.add_argument('input_folder', type=str, help='Folder with .tif files for using as input.')
    parser.add_argument('--tile', '-t', type=str, choices=['00000','12544'], default='00000', help='Tile to concatenate. Default: *00000.tif.')
    parser.add_argument('--output_folder', '-o', type=str, default='results', help='Output folder. Default: results.')
    parser.add_argument('--index', '-i', choices=all_index, type=str, nargs='+', default=None, help='Index to calculate. If no one is set, all are calculated.')
    parser.add_argument('--bucket', '-b', default=None, type=str, help='Bucket blob for saving the output.')
    parser.add_argument('--ram', '-r', default=256, type=int, help='Available memory for processing (in MB), default 256.')
    args = parser.parse_args()

    if not args.index:
        args.__setattr__('index',all_index)

    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)
        
    for i in args.index:
        concatenate(args.input_folder, args.tile, i, args.output_folder, args.bucket)

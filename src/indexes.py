import os
import subprocess
from typing import *
from glob import glob

from src.utils import save_path_in_bucket
from src.indexes_definition import indexes


def calc_index(input_folder:str, index:str, ram:int, bucket:Union[str,None]=None)->None:
    '''
        Parameters
        ----------
            input_folder: str
                Folder with subfolders and .tif files.

            index: str
                Spectral index.
            
            ram: int, default: 256
                Available memory for processing (in MB).

            bucket: str, default: None
                GCP Bucket location URI for output file.
                If None, output file is not saved in bucket.

        Returns
        -------
            None
    '''
    images = glob(f'{input_folder}/*/*[0-9].tif')
    
    for image in images:
        fname, ext = os.path.splitext(image)
        im_out_fname = '{im}_{index}.tif'.format(im=fname, index=index.lower())
        cmd = """bash -c 'source ~/OTB-8.0.1-Linux64/otbenv.profile; \
        otbcli_BandMath -il {im} -out {im_out} -exp {form} -ram {memoria}'
        """.format(im=image, im_out=im_out_fname, form=indexes.get(index), memoria = ram)
        subprocess.run(cmd, shell=True)
        if bucket:
            save_path_in_bucket(im_out_fname, bucket)
            os.remove(im_out_fname)
    print(f'\n***** {index} calculated.\n')


if __name__ == '__main__':
    
    import argparse

    all_index = list(indexes.keys())

    parser = argparse.ArgumentParser(
        prog='Calculador de índices espectrales',
        description='Calcula los índices espectrales NDVI, NDVI_a, NDSI, NBI, NDWI (Gao), DNWI (McFeeters) y muchos más'
    )
    parser.add_argument('input_folder', type=str, help='Folder with .tif files for using as input.')
    parser.add_argument('--index', '-i', choices=all_index, type=str, nargs='+', default=None, help='Index to calculate. If no one is set, all are calculated.')
    parser.add_argument('--bucket', '-b', default=None, type=str, help='Bucket blob for saving the output.')
    parser.add_argument('--ram', '-r', default=256, type=int, help='Available memory for processing (in MB), default 256.')
    args = parser.parse_args()

    if not args.index:
        args.__setattr__('index',all_index)

    for i in args.index:
        calc_index(
            input_folder=args.input_folder,
            index=i,
            bucket=args.bucket,
            ram=args.ram
        )

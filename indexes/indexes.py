import os
import subprocess
from glob import glob

# chequear que sean estas las bandas correctas
# las fórmulas ya tienen la corrección del raster (bandas-1)
# consultar si NDSI y NBI usand SWIR 2 y NDWI_gao SWIR 1
# esto es lo que nos dejó Fede: (consultar)
# NDVI:(im1b7-im1b3)/(im1b7+im1b3)

indexes = {
        "NDVI":"(im1b4-im1b3)/(im1b4+im1b3)",
        "NDVI_a":"(im1b5-im1b3)/(im1b5+im1b3)",
        "NDSI":"(im1b2-im1b7)/(im1b2+im1b7)",
        "NBI":"(im1b4-im1b7)/(im1b4+im1b7)",
        "NDWI_gao":"(im1b4-im1b6)/(im1b4+im1b6)",
        "NDWI_mcfeeters":"(im1b2-im1b4)/(im1b2+im1b4)"
}

def save_in_bucket(file_path:str, bucket:str):
    cmd = """gsutil cp {file} {bucket}""".format(file=file_path, bucket=bucket)
    subprocess.run(cmd, shell=True)


def calc_index(input_folder:str, index:str, bucket:str=None):
    
    images = glob(f'{input_folder}/*/*[0-9].tif')
    
    for image in images:
        print(images)
        fname, ext = os.path.splitext(image)
        im_out_fname = '{im}_{index}.tif'.format(im=fname, index=index.lower())
        cmd = """bash -c 'source ~/OTB-8.0.1-Linux64/otbenv.profile; \
        otbcli_BandMath -il {im} -out {im_out} -exp "{form}"'
        """.format(im=image, im_out=im_out_fname, form=indexes.get(index))
        subprocess.run(cmd, shell=True)
        if bucket:
            save_in_bucket(im_out_fname, bucket)
            os.remove(im_out_fname)
    print(f'\n***** {index} calculated.\n')


if __name__ == '__main__':
    
    import argparse

    all_index = list(indexes.keys())

    parser = argparse.ArgumentParser(
        prog='Calculador de índices espectrales',
        description='Calcula los índices espectrales NDVI, NDVI_a, NDSI, NBI, NDWI (Gao) y DNWI (McFeeters).'
    )
    parser.add_argument('input_folder', type=str, help='Folder with .tif files for using as input.')
    parser.add_argument('--index', '-i', choices=all_index, type=str, nargs='+', default=None, help='Index to calculate. If no one is set, all are calculated.')
    parser.add_argument('--bucket', '-b', default=None, type=str, help='Bucket blob for saving the output.')
    args = parser.parse_args()

    if not args.index:
        args.__setattr__('index',all_index)

    for i in args.index:
        calc_index(
            input_folder=args.input_folder,
            index=i,
            bucket=args.bucket
        )

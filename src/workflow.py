import os
import re
import argparse

from src.obtcli_command import run_command

parser = argparse.ArgumentParser()
parser.add_argument('concat_folder', help='Folder with (only) concat files. If there is more than one concat file (one per tile), make the workflow for all of them.')
parser.add_argument('vec_shp', help='Path to file with labels.')
parser.add_argument('field', choices=['id','DN'], help='Column name with label for sample selection and extraction.')
parser.add_argument('--ram', '-r', default=1000, help='Ram. Default: 1000.')
args = parser.parse_args()

root_folder = args.concat_folder.split('/')[0]
vec_spec = os.path.splitext(os.path.basename(args.vec_shp))[0]

files = os.listdir(args.concat_folder)

for f in files:
    file_path = os.path.join(args.concat_folder, f)

    file_id = re.search(r'\d+',f).group()

    # PolygonClassStatistics
    print('**********************************')
    print('***** PolygonClassStatistics *****')
    print('**********************************')
    output_polygon = os.path.join(root_folder,f'polygonclass_{vec_spec}')
    os.makedirs(output_polygon, exist_ok=True)
    output_file_polygon = os.path.join(
        output_polygon,
        f'{file_id}_classes_stats.xml'
    )
    run_command(
        method='PolygonClassStatistics',
        input_file=file_path,
        vec=args.vec_shp,
        field=args.field,
        output_file=output_file_polygon,
        ram=args.ram
    )

    print(f'\n*** PolygonClassStatistics\n==> OUTPUT SAVED IN:')
    print(f'\t- {output_file_polygon}\n')

    # SampleSelection
    print('***************************')
    print('***** SampleSelection *****')
    print('***************************')
    output_selection = os.path.join(root_folder,f'selection_{vec_spec}')
    os.makedirs(output_selection, exist_ok=True)
    output_selection_rates = os.path.join(
        output_selection,
        f'{file_id}_rates.csv'
    )
    output_selection_samples = os.path.join(
        output_selection,
        f'{file_id}_sample.sqlite'
    )
    run_command(
        method='SampleSelection',
        input_file=file_path,
        vec=args.vec_shp,
        classes_stats=output_file_polygon,
        field=args.field,
        strategy='total',
        output_rates=output_selection_rates,
        output_sqlite=output_selection_samples,
        ram=args.ram
    )

    print(f'\n*** SampleSelection\n==> OUTPUT SAVED IN:')
    print(f'\t- {output_selection_rates}\n')
    print(f'\t- {output_selection_samples}\n')

    # SampleExtraction
    print('****************************')
    print('***** SampleExtraction *****')
    print('****************************')
    run_command(
        method='SampleExtraction',
        input_file=file_path,
        vec=output_selection_samples,
        field=args.field.lower(),
        ram=args.ram
    )

    print(f'\n*** SampleExtraction\n==> OUTPUT SAVED IN:')
    print(f'\t- {output_selection_samples}\n')

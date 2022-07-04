import os
import re
import argparse

from src.obtcli_command import run_command

parser = argparse.ArgumentParser()
parser.add_argument('concat_folder', help='Folder with (only) concat files. If there is more than one concat file (one per tile), make the workflow for all of them.')
parser.add_argument('verdad_campo', help='Folder with true labels.')
parser.add_argument('--ram', '-r', default=1000, help='Ram. Default: 1000.')
args = parser.parse_args()

root_folder = args.concat_folder.split('/')[0]
verdad_campo_folder = args.verdad_campo.strip('/')
verdad_campo_file = os.path.join(verdad_campo_folder,'verdad_campo.shp')

files = os.listdir(args.concat_folder)

for f in files:
    file_path = os.path.join(args.concat_folder, f)

    file_id = re.search(r'\d+',f).group()

    # PolygonClassStatistics
    print('**********************************')
    print('***** PolygonClassStatistics *****')
    print('**********************************')
    output_polygon = os.path.join(root_folder,'polygonclass')
    os.makedirs(output_polygon, exist_ok=True)
    output_file_polygon = os.path.join(
        output_polygon,
        f'{file_id}_classes_stats.xml'
    )
    run_command(
        method='PolygonClassStatistics',
        input_file=file_path,
        vec=verdad_campo_file,
        field='id',
        output_file=output_file_polygon,
        ram=args.ram
    )

    print(f'\n*** PolygonClassStatistics\n==> OUTPUT SAVED IN:')
    print(f'\t- {output_file_polygon}\n')

    # SampleSelection
    print('***************************')
    print('***** SampleSelection *****')
    print('***************************')
    output_selection = os.path.join(root_folder,'selection')
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
        vec=verdad_campo_file,
        classes_stats=output_file_polygon,
        field='id',
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
        field='id',
        ram=args.ram
    )

    print(f'\n*** SampleExtraction\n==> OUTPUT SAVED IN:')
    print(f'\t- {output_selection_samples}\n')

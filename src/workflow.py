import re
import subprocess
from string import Template

options = {
    "PolygonClassStatistics": "-in $input_file -vec $vec -field  $fileid -out $output_file",
    "SampleSelection": "-in $input_file -vec $vec -instats $classes_stats -field $fieldid -strategy $strategy -outrates $output_rates -out $output_sqlite",
    "SampleExtraction": "-in $input_file -vec $vec -outfield prefix -outfield.prefix.name band_ -field $field",
    "ComputeImageStatistics": "-il $input_file -out.xml $output_xml_file"
"
}

def select_command(method:str):
    settings_templ = options.get(method)
    cmd = f"""
    bash -c 'source ~/OTB-8.0.1-Linux64/otbenv.profile;
    otbcli_{method} {settings_templ}'
    """
    return cmd

def run_command(**kwargs):
    method = kwargs.get('method')
    command_templ = select_command(method)
    command = Template(command_templ).safe_substitute(**kwargs)
    subprocess.run(command, shell=True)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='method', description='Método a ejecutar.')

    for method, command in options.items():

        command_templ = select_command(method)
        parser_method = subparsers.add_parser(
            method,
            help=f'Ejecuta el método {method}',
            description=f'Genera el comando {command_templ} con los reemplazos indicados (respetar el orden).'
        )
        parameters = re.finditer(r'\$(\w*\b)', command_templ)
        for p in parameters:
            parser_method.add_argument(p.group(1))
        
    args = parser.parse_args()
    run_command(**vars(args))

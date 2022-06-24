import os
import subprocess


def save_path_in_bucket(file_path:str, bucket:str)->None:
    folder_path = os.path.dirname(file_path)
    bucket_blob = os.path.join(bucket, folder_path)
    save_file_in_bucket(file_path, bucket_blob)

def save_file_in_bucket(file_path:str, bucket:str)->None:
    file_name = os.path.basename(file_path)
    bucket_blob = os.path.join(bucket, file_name)
    cmd = """gsutil -m cp {file} {blob}""".format(file=file_path, blob=bucket_blob)
    subprocess.run(cmd, shell=True)


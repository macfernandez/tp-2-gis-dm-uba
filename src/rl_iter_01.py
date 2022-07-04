#!/usr/bin/env python
# coding: utf-8

import os
import json
import joblib
import numpy as np
import pandas as pd
from glob import glob
from tqdm import tqdm
from pyproj import CRS
from sqlite3 import connect
from sklearn.linear_model import LogisticRegression

from src.utilities import *

# --- ARMADO DEL DATASET

def load_dataset(sqlite_folder:str)->pd.DataFrame:
    sqlite_files = glob(f'{sqlite_folder}/*.sqlite')
    data = pd.DataFrame()
    for sf in sqlite_files:
        cnx = connect(sf)
        df = pd.read_sql_query("SELECT * FROM output", cnx)
        data = pd.concat([data, df], ignore_index=True)
    print(f'Dataset para primera iteración - shape: {data.shape}')
    return data

# --- TARGET VALUE COUNTS

def count_target_values(df:pd.DataFrame, target:str)->pd.DataFrame:
    target_count = (
        df[target]
        .value_counts()
        .to_frame()
        .rename(columns={target:'pixeles'})
        .T
    )
    print(f'Target value counts - CULTIVOS')
    print(target_count)

# ----- TRAINING

def train_rl_model(df:pd.DataFrame)->str:
    X = df.filter(regex='band_').to_numpy()
    y = df['id'].to_numpy()

    model = LogisticRegression(
        random_state=20220707,
        multi_class='multinomial',
        max_iter=300
    )

    os.makedirs('model', exist_ok=True)
    with open('model/rl_parameters.json','w') as f:
        json.dump(model.get_params(), f, ensure_ascii=False, indent=4)

    model.fit(X, y)

    output_file = 'model/rl_iter_01.joblib'
    _ = joblib.dump(model,'model/rl_iter_01.joblib')
    print(f'RL trained and saved in {output_file}.')
    return output_file

# ----- PREDICTION

def make_prediction(model_path:str, data_folder:str)->None:
    model = joblib.load(model_path)

    os.makedirs('predictions/', exist_ok=True)
    tif_files = glob(f'{data_folder}/*')

    for tile in tif_files:
        width, height, transform = metadata_from_tile(tile)
        windows = sliding_windows(100, 100, width, height)
        preds = np.empty((10000,7))
        windows =list(windows) 
        for window,_ in tqdm(windows, total=len(windows)):
            img_df = create_windowed_dataset(tile, window)
            res = model.predict_proba(img_df).astype(np.float64)
            preds = np.append(preds, res, axis = 0)
        tile_name = os.path.basename(tile).replace('.tif','').strip()
        with open(f'predictions/{tile}.npy', 'wb') as f:
            np.save(f, preds)
            print(f'Prediction for {tile} already made.')


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('sqlite_folder', help='Folder with extraced .sqlite for training.')
    parser.add_argument('tif_folder', help='Folder with concated .tif for training.')
    args = parser.parse_args()

    training = load_dataset(args.sqlite_folder)
    _ = count_target_values(training, 'cultivo')
    model_path = train_rl_model(training)
    make_prediction(model_path, args.tif_folder)


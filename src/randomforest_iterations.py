#!/usr/bin/env python
# coding: utf-8

import os
import re
import json
import shutil
import joblib
import rasterio
import argparse
import numpy as np
import pandas as pd
from glob import glob
from pyproj import CRS
from copy import deepcopy
from sqlite3 import connect
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

from src.utilities import *


parser = argparse.ArgumentParser()
parser.add_argument('train_folder', help='Path to folder with .sqlite for training.')
parser.add_argument('pred_folder', help='Path to folder with .sqlite for prediction.')
parser.add_argument('model_parameters', help='Path to file with model parameters.')
parser.add_argument('output_folder', help='Path to folder for saving model outputs.')
parser.add_argument('--thresholds','-t', default=[0.6], nargs='+', help='Cut off thresholds.')
args = parser.parse_args()

# Conjunto de entrenamiento
train_sqlite_files = glob(f'{args.train_folder}/*.sqlite')

train_data = pd.DataFrame()

for sf in train_sqlite_files:
    file_name = os.path.basename(sf)
    tile = re.search(r'\d+',file_name).group()
    cnx = connect(sf)
    df = pd.read_sql_query("SELECT * FROM output", cnx)
    df['tile_file'] = tile
    train_data = pd.concat([train_data, df], ignore_index=True)

# Conjunto de predicción
pred_sqlite_files = glob(f'{args.pred_folder}/*.sqlite')

pred_data = pd.DataFrame()

for sf in pred_sqlite_files:
    file_name = os.path.basename(sf)
    tile = re.search(r'\d+',file_name).group()
    cnx = connect(sf)
    df = pd.read_sql_query("SELECT * FROM output", cnx)
    df['tile_file'] = tile
    df.drop(columns=['id'], inplace=True)
    pred_data = pd.concat([pred_data, df], ignore_index=True)

# train_data está dentro de pred_data
# saco esas filas de pred_data
# así no predecimos con lo mismo con lo que entrenamos
merged_data = pred_data.merge(train_data[['ogc_fid','tile_file','cultivo','id']], how='left', on=['ogc_fid','tile_file'], indicator=True)
train_data = merged_data[merged_data._merge=='both'].drop(columns=['_merge']).assign(id=lambda x:x.id.astype('int'))
pred_data = merged_data[merged_data._merge=='left_only'].drop(columns=['_merge'])

print(f'*** Training data shape: {train_data.shape}')
print(f'*** Prediction data shape: {pred_data.shape}')

# Entrenamiento del modelo

map_id2cultivo = dict((
    train_data[['id','cultivo']]
    .drop_duplicates()
    .assign(id=lambda x: x.id.astype('int'))
    .itertuples(index=False, name=None))
)

le = LabelEncoder()
le.fit(train_data.id)

map_le2id = dict(zip(le.transform(le.classes_), list(map(int,le.classes_))))
train_data['id_le'] = le.transform(train_data.id)

with open(args.model_parameters,'r') as f:
    parameters = json.load(f)

thresholds = args.thresholds

for threshold in thresholds:
    
    iter_train_data = deepcopy(train_data)
    iter_pred_data = deepcopy(pred_data)
    
    print(f'+++++ PREDICCIONES PARA THRESHOLD {threshold}')
    
    threshold_folder = os.path.join(args.output_folder, f'threshhold_{threshold}')
    if os.path.exists(threshold_folder):
        shutil.rmtree(threshold_folder)
        os.mkdir(threshold_folder)
    
    i = 0
    while True:
        
        # arma carpeta para el output (i aumenta con las iteraciones)
        n_iter = '{0:03d}'.format(i)
        output_folder = os.path.join(threshold_folder,f'randomforest_iterations_{n_iter}')
        
        os.makedirs(output_folder, exist_ok=True)
        
        # toma los datasets
        columns = iter_train_data.filter(regex='band_').columns.to_list()
        X_train = iter_train_data.filter(regex='band_').fillna(-99999).to_numpy()
        y_train = iter_train_data.id_le.to_numpy()
        X_pred = iter_pred_data.filter(regex='band_').fillna(-99999).to_numpy()
        
        # instancia y entrena el modelo
        model = RandomForestClassifier(**parameters)
        model.fit(X_train, y_train)
        output_model_file = os.path.join(output_folder, f'model_{n_iter}.joblib')
        _ = joblib.dump(model, output_model_file)
        
        # predice
        probas = model.predict_proba(X_pred)
        output_proba_file = os.path.join(output_folder, f'probas_{n_iter}.npy')
        np.save(output_proba_file, probas)
        predictions = iter_pred_data.assign(pred_class=probas.argmax(axis=1), pred_score=probas.max(axis=1))
        
        # separa entre nuevo train y nuevo pred
        add_to_train = predictions.query(f'pred_score >= {threshold}').copy()
        continue_pred = predictions.query(f'pred_score < {threshold}').copy()
        train_data_len, add_to_train_len , continue_pred_len = iter_train_data.shape[0], add_to_train.shape[0] , continue_pred.shape[0]
        output_pixels_file = os.path.join(output_folder, f'pixels_{n_iter}.csv')
        (
            pd.DataFrame(
                [
                    [f'De entrenamiento', train_data_len],
                    [f'Con proba>={threshold}', add_to_train_len],
                    [f'Con proba<{threshold}', continue_pred_len]
                ],
                columns=['Pyxels_type','Pixels']
            )
            .to_csv(output_pixels_file, index=False)
        )
        
        output_deptos_file = os.path.join(output_folder, f'pred_deptos_{n_iter}.csv')
        (
            pd.DataFrame(
                [
                    [f'De entrenamiento', train_data_len],
                    [f'Con proba>={threshold}', add_to_train_len],
                    [f'Con proba<{threshold}', continue_pred_len]
                ],
                columns=['Pyxels_type','Pixels']
            )
            .to_csv(output_pixels_file, index=False)
        )
        
        # pasa predicción a las columna id (target)
        # y lo agrega al train original
        add_to_train['id_le'] = add_to_train['pred_class']
        add_to_train['id'] = add_to_train.id_le.apply(lambda x: map_le2id.get(x))
        add_to_train['cultivo'] = add_to_train.id.apply(lambda x: map_id2cultivo.get(x))

        iter_deptos_prediction = os.path.join(output_folder,f'randomforest__deptos_prediction_{n_iter}.csv')
        (
            add_to_train
            .groupby(['cultivo','nombre'], as_index=False)
            .size()
            .rename(columns={'size':'pixels','nombre':'departamento'})
            .assign(ha=lambda x: x.pixels*0.04)
            .to_csv(iter_deptos_prediction, index=False)
        )
        iter_train_data =iter_train_data.append(add_to_train, ignore_index=True)
        iter_pred_data = continue_pred
        
        # imprime información
        print('''\n*** ITERACIÓN #{0:03d}
        - Modelo guardado en {1}
        - Probabilidades guardadas en {2}
        - Pixeles de entrenamiento: {3}
        - Pixeles con proba>={4}: {5}
        - Pixeles con proba<{4}: {6}'''.format(i, output_model_file, output_proba_file, train_data_len, threshold, add_to_train_len , continue_pred_len))
        i += 1
        if (add_to_train_len == 0) or (continue_pred_len == 0):
            break

    # reemplaza na en columna pred_class con 'vc_original'
    # (los pixeles que no tiene pred_class son los pieles de verdad de campo originales)
    # y guarda la predicción final
    nueva_vc_prediction = os.path.join(threshold_folder,f'randomforest_nueva_vc_prediction.csv')
    iter_train_data.to_csv(nueva_vc_prediction)
    nueva_vc_deptos = os.path.join(threshold_folder,f'randomforest_nueva_vc_deptos.csv')
    (
        iter_train_data
        .groupby(['cultivo','nombre'], as_index=False)
        .size()
        .rename(columns={'size':'pixels','nombre':'departamento'})
        .assign(ha=lambda x: x.pixels*0.04)
        .to_csv(nueva_vc_deptos, index=False)
    )
    
    
    # pasa predicción a las columna id (target)
    # y agrega las predicciones que no superaron el umbral a la nueva verdad de campo
    # (i.e. a las que sí lo superaron)
    # así, tenemos el conjunto completo y calculamos las ha sobre el total
    continue_pred['id_le'] = continue_pred['pred_class']
    continue_pred['id'] = continue_pred.id_le.apply(lambda x: map_le2id.get(x))
    continue_pred['cultivo'] = continue_pred.id.apply(lambda x: map_id2cultivo.get(x))
    
    total_final_prediction = os.path.join(threshold_folder,f'randomforest_total_final_prediction.csv')
    total_prediction = iter_train_data.append(continue_pred)
    total_prediction.to_csv(total_final_prediction)
    
    total_final_deptos = os.path.join(threshold_folder,f'randomforest_total_final_deptos.csv')
    (
        total_prediction
        .groupby(['cultivo','nombre'], as_index=False)
        .size()
        .rename(columns={'size':'pixels','nombre':'departamento'})
        .assign(ha=lambda x: x.pixels*0.04)
        .to_csv(total_final_deptos, index=False)
    )

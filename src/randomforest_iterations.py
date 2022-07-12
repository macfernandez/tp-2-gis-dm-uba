#!/usr/bin/env python
# coding: utf-8

import os
import re
import json
import shutil
import joblib
import rasterio
import argparse
import logging
import numpy as np
import pandas as pd
from glob import glob
from pyproj import CRS
from copy import deepcopy
from sqlite3 import connect
from tqdm.notebook import tqdm
from sklearn.metrics import confusion_matrix
from sklearn.metrics import cohen_kappa_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.utilities import *


parser = argparse.ArgumentParser()
parser.add_argument('train_folder', help='Path to folder with .sqlite for training.')
parser.add_argument('pred_folder', help='Path to folder with .tif for prediction.')
parser.add_argument('model_parameters', help='Path to file with model parameters.')
parser.add_argument('output_folder', help='Path to folder for saving model outputs.')
args = parser.parse_args()

args_train_folder = args.train_folder.strip('/')
args_pred_folder = args.pred_folder.strip('/')
args_output_folder = args.output_folder.strip('/')

train_sqlite_files = glob(f'{args_train_folder}/*.sqlite')

train_data = pd.DataFrame()

for sf in train_sqlite_files:
    file_name = os.path.basename(sf)
    tile = re.search(r'\d+',file_name).group()
    cnx = connect(sf)
    df = pd.read_sql_query("SELECT * FROM output", cnx)
    df['tile_file'] = tile
    train_data = pd.concat([train_data, df], ignore_index=True)

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


def metadata_from_tile(in_raster):
    with rasterio.open(in_raster) as src:
        return(src.width, src.height, src.transform)

def sliding_windows(size, step_size, width, height, whole=False):
    """Slide a window of +size+ by moving it +step_size+ pixels"""
    w, h = size, size
    sw, sh = step_size, step_size
    end_i = height - h if whole else height
    end_j = width - w if whole else width
    for pos_i, i in enumerate(range(0, end_i, sh)):
        for pos_j, j in enumerate(range(0, end_j, sw)):
            real_w = w if whole else min(w, abs(width - j))
            real_h = h if whole else min(h, abs(height - i))
            yield Window(j, i, real_w, real_h), (pos_i, pos_j)


next_train = pd.DataFrame()
i = 0
while True:
    
    logging.warning(f'##### INICIANDO ITERACIÓN #{i}')
    # si el entrenamiento de la próxima iteración es mayor (en cantidad)
    # a la data de entrenamiento, entonces toma el entrenamiento de la próxima
    # iteración
    # si no, toma la data de entrenamiento original (verdad de capo original)
    # el entrenamiento de la próxima iteración es un df que se va enriqueciendo
    # con la nueva verdad de campo predicha
    # hago esto así porque, usando los tif, no sé cómo verificar si los pixeles
    # están o no en la verdad de campo (entonces no quiero agregar la nueva
    # verdad de camp al df que ya contiene la verdad de campo original
    # porquee estaría duplicando los datos)
    # así, primera iteración va a usar la data original y ya en la segunda
    # iteración va a tomar el entrenamiento con la nueva verdad
    if next_train.shape[0] >= train_data.shape[0]:
        train_data = next_train

    # arma carpeta para el output (i aumenta con las iteraciones)
    n_iter = '{0:03d}'.format(i)
    output_folder = os.path.join(args_output_folder, f'randomforest_iterations_{n_iter}')
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)
    
    logging.warning(f'[{n_iter}] ---> Entrenamiento de modelo para definir umbral')
    # segmenta en train y test
    X = train_data.filter(regex='band_').fillna(-99).to_numpy()
    y = train_data['id_le'].to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=.3, random_state=20220714, shuffle=True, stratify=y
    )
    
    # instancia y entrena el modelo con set de entrenamiento
    model = RandomForestClassifier(**parameters)
    model.fit(X_train, y_train)
    
    logging.warning(f'[{n_iter}] ---> Predicción de probabilidades para definir umbral')
    # predice sobre el conjunto de testeo
    probas = model.predict_proba(X_test)
    output_proba_file = os.path.join(output_folder, f'probas_{n_iter}.npy')
    np.save(output_proba_file, probas)
    
    y_hat = probas.argmax(axis=1)
    
    logging.warning(f'[{n_iter}] ---> Generación de métricas de modelo para definir umbral')
    # guarda métricas
    cmatrix = confusion_matrix(y_test, y_hat, normalize='all')
    output_cmpatrix_file = os.path.join(output_folder, f'cmatrix_{n_iter}.npy')
    np.save(output_cmpatrix_file, cmatrix)
    
    report = classification_report(y_test, y_hat, output_dict=True)
    output_report_file = os.path.join(output_folder, f'report_{n_iter}.json')
    with open(output_report_file, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    
    kappa = cohen_kappa_score(y_test, y_hat)
    output_kappa_file = os.path.join(output_folder, f'kappa_{n_iter}.txt')
    with open(output_kappa_file, 'w') as f:
        _ = f.write(str(kappa))
    
    # evalúa cantidad de aciertos y errores por nivel de confianza (cada 0.05)
    predictions = pd.DataFrame({
        'success':y_test==y_hat,
        'score':probas.max(axis=1),
    })
    hits, confidence = np.histogram(predictions[predictions.success==True].score, 20, (0,1))
    misses, _ = np.histogram(predictions[predictions.success==False].score, 20, (0,1))
    hits_misses_df = (
        pd
        .DataFrame({'hit':hits, 'miss':misses, 'confidence':np.round(confidence[:-1], 2)})
    )
    output_success_file = os.path.join(output_folder, f'hits_misses_{n_iter}.csv')
    hits_misses_df.to_csv(output_success_file, index=False)
    
    logging.warning(f'[{n_iter}] ---> Seección de umbral')
    # selecciona el umbral
    # umbral = score cuya cantidad de aciertos duplique la cantidad de errores + 1
    threshold = hits_misses_df.loc[hits_misses_df.hit>(hits_misses_df.miss+1)*2,'confidence'].min()
    output_threshold_file = os.path.join(output_folder, f'threshold_{n_iter}.txt')
    with open(output_threshold_file, 'w') as f:
        _ = f.write(str(threshold))

    logging.warning(f'[{n_iter}] ---> Entrenamiento de modelo para predicción de clases')
    # instancia y entrena el modelo con set de entrenamiento + validación
    iter_X = train_data.filter(regex='band_').fillna(-99999).to_numpy()
    iter_y = train_data['id_le'].to_numpy()

    model = RandomForestClassifier(**parameters)
    model.fit(iter_X, iter_y)
    output_model_file = os.path.join(output_folder, f'model_{n_iter}.joblib')
    _ = joblib.dump(model, output_model_file)
    
    # levanta los .tif para predecir
    pred_tif = glob(f'{args_pred_folder}/*.tif')
    
    vc_len = X_train.shape[0] + X_test.shape[0]
    new_vc_len = 0

    logging.warning(f'[{n_iter}] ---> Predicción de clases para rásters')
    for tif in pred_tif:
        # detecta nombre del raster
        # 12544.tif o 00000.tif
        name_raster = os.path.basename(tif)
        
        logging.warning(f'[{n_iter}] +++ PREDICCIÓN PARA TILE: {name_raster}')
        
        # levanta la metadata del tif
        width, height, transform = metadata_from_tile(tif)
        # arma las ventanas de 100x100
        windows = sliding_windows(100, 100, width, height)
    
        # si no está en la primera iteración
        # busca el raster para enmascarar de la iteración anterior
        if i>0:
            prev_i = i-1
            prev_iter = '{0:03d}'.format(prev_i)
            prev_folder = output_folder.replace(n_iter, prev_iter)
            prev_tif = os.path.join(prev_folder, name_raster)
        
        out_raster = os.path.join(output_folder, name_raster)
        with rasterio.open(
            out_raster, 'w', driver='GTiff', count=1,
            width=width, height=height, dtype=np.float64, transform=transform,
            crs=CRS.from_epsg(4326), compress='lzw') as dst:
            
            windows = list(windows)
            windows_len = len(windows)
            wn = 0
            for window in windows:
                logging.warning(f'[{n_iter}] ... Prediciendo ventana {wn} de {windows_len}')
                wn +=1
                
                win=window[0]
                # abre ventana en el raster original
                src = rasterio.open(tif)
                img = src.read(window=win)
                r,m,n = img.shape
                
                # arma un dataframe con la data para predecir
                # shape: 10000 filas (100x100 pixeles) x 28 columnas (bandas)
                tif_df = (
                    pd.DataFrame(img.reshape(r,m*n))
                    .T.fillna(-99)
                )
                tif_df.rename(columns={col:f'band_{col}' for col in tif_df.columns}, inplace=True)
                
                # si no está en la primera iteración
                # arma un dataframe con la data para enmascarar
                # shape: 10000 filas (100x100 pixeles) x 28 columnas (bandas)
                if i>0:
                    # abre ventana en el raster de la iteración previa
                    # para enmascarar
                    src_mask = rasterio.open(prev_tif)
                    mask = src_mask.read(window=win) 
                    mask_r, mask_m, mask_n = mask.shape
                    mask_df = pd.DataFrame(mask.reshape(mask_r,mask_m*mask_n)).T
                    tif2predict = deepcopy(tif_df[mask_df.id==-99])
                # si está en la primera iteración
                # toma el tif completo
                else:
                    tif2predict = deepcopy(tif_df)

                #img_df.rename(columns={col:f'band_{col}' for col in img_df.columns}, inplace=True)
                # agrega columna con predicciones
                iter_prediction = model.predict_proba(tif2predict.to_numpy())
                tif2predict['id_le'] = iter_prediction.argmax(axis=1)
                tif2predict['score'] = iter_prediction.max(axis=1)

                # si la banda_1==-99
                # ese pixel es nan (no tiene info)
                # entonces indicame con un valor que ese no me interesa (-111)
                # este valor no se va a tener en cuenta después para enmascarar
                tif2predict.loc[tif2predict.band_1==-99,'id_le'] = -111

                # si el score de la predicción supera al umbral
                # y el pixel no es nulo
                # agrega esa info al entrenamiento de la próxima iteración
                new_vc = tif2predict[(tif2predict.score>=threshold) & (tif2predict.id_le!=-111)]
                new_vc['id_le'] = new_vc.id_le.astype('int')
                next_train = pd.concat([next_train, new_vc])
                new_vc_len += new_vc.shape[0]
                
                # asigna id real
                # enmascara las predicciones cuyo score no supera al umbral (-99)
                # y lo guarda en un nuevo .tif
                if i>0:
                    # si el id_le está en el diccionario map_le2id, asignale el id mapeado
                    # si no está (-111 no está), dejá ese
                    # lo hago así porque después busco los -99 para mapear
                    # los que son -111 ya ni los miro (son nulos)
                    tif_df.loc[mask_df.id==-99, 'id'] = tif2predict.id_le.apply(lambda x:map_le2id.get(x, x))
                    tif_df.loc[mask_df.id==-99, 'score'] = tif2predict.score
                else:
                    tif_df['id'] = tif2predict.id_le.apply(lambda x:map_le2id.get(x, x))
                    tif_df['score'] = tif2predict.score
                tif_df.loc[(tif_df.score<threshold) & (tif_df.id!=-111), 'id'] = -99
                tif_class = np.expand_dims(tif_df.id.to_numpy().reshape(n,m), axis=0)
                dst.write(tif_class, window=win)
                
                # cuando se hace la predicción hay que revisar si hay un .tif del modelo para enmascarar
                # (solo se predicen los pixeles que tengan NA)          
    
    output_vc_file = os.path.join(output_folder, f'verdad_campo_{n_iter}.txt')
    with open(output_vc_file, 'w') as f:
        _ = f.write(f'''verdad_campo_entrenamiento,{vc_len}\nvedad_campo_nueva{new_vc_len}\n''')
    # imprime información
    logging.warning(f'''\n*** ITERACIÓN #{n_iter}
    - Pixeles de entrenamiento: {X_train.shape[0]}
    - Pixeles de validación: {X_test.shape[0]}
    - Probabilidades sobre train guardadas en {output_proba_file}
    - Umbral definido: {threshold}
    - Pixeles del modelo final: {vc_len}
    - Modelo guardado en: {output_model_file}
    - Nueva verdad de campo predicha: {new_vc_len}''')
    i += 1

    #if new_vc_len == 0:
    #    break

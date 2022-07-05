#!/usr/bin/env python
# coding: utf-8

import os
import joblib
import argparse
import numpy as np
import pandas as pd
from glob import glob
import seaborn as sns
from sqlite3 import connect
import matplotlib.pyplot as plt
    
    
parser = argparse.ArgumentParser()
parser.add_argument('sqlite_folder', help='Folder with extraced .sqlite for training.')
parser.add_argument('model', help='Path to .joblib model file.')
args = parser.parse_args()


# ----- LOAD TRAININGSET

sqlite_folder = args.sqlite_folder.strip('/')
sqlite_files = glob(f'{sqlite_folder}/*.sqlite')

data = pd.DataFrame()

for sf in sqlite_files:
    cnx = connect(sf)
    df = pd.read_sql_query("SELECT * FROM output", cnx)
    data = pd.concat([data, df], ignore_index=True)

X = data.filter(regex='band_').to_numpy()
y = data['id'].to_numpy()

# ----- LOAD MODEL

model = joblib.load(args.model)

# ----- PREDICT

model_folder = os.path.dirname(args.model)
output_folder = os.path.join(model_folder, 'predictions')

os.makedirs(output_folder, exist_ok=True)

y_hat = model.predict_proba(X)

probas_file_path = os.path.join(output_folder,'randomforest_probas_train.npy')
with open(probas_file_path, 'wb') as f:
    np.save(f, y_hat)


max_probas = y_hat.max(axis=1)
classes = [model.classes_[a] for a in y_hat.argmax(axis=1)]

data = data.assign(pred_class=classes, pred_score=max_probas)

true_preds = data[data.id==data.pred_class]
min_score = true_preds.pred_score.min()

minscore_file_path = os.path.join(output_folder,'randomforest_minscore_train.npy')
with open(minscore_file_path, 'wb') as f:
    np.save(f, min_score)

# ----- CUTOFF

fig_file_path = os.path.join(output_folder,'randomforest_train_cutoff.png')

cutt_off = []
samples = []
for i in np.linspace(0,1,20):
    data['mask'] = data.pred_score.apply(lambda x: True if x>1-i else False)
    cantidades = data[(data.id==data.pred_class) & (data['mask']==True)].shape[0]
    cutt_off.append(i)
    samples.append(cantidades)


sns.set_style('whitegrid')
fig, ax = plt.subplots(figsize=(6,4))
sns.lineplot(x=cutt_off, y=samples)
plt.xlabel('Cut-off')
plt.ylabel('Samples')
plt.title('Cut-off vs. Samples', fontsize=18)
plt.savefig(fig_file_path)


print(f'\n{len(true_preds)}/{len(data)} pixeles fueron correctamente predichos.')
print(f'El mínimo score de predicción fue: {min_score}')
print(f'Los resultados fueron guardados en {output_folder}')

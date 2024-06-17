
import re
import os
import json
import numpy as np
import pandas as pd
import seaborn as sns
from glob import glob
from sqlite3 import connect
import matplotlib.pyplot as plt

cmatrix = np.load('model/cmatrix_000.npy')

map_id2cultivo = {3: 'MAIZ', 1: 'SOJA', 2: 'MAIZ', 20: 'CAMPONATUR', 5: 'GIRASOL', 10: 'ALFALFA', 4: 'SOJA'}
map_le2id = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 10, 6: 20}

fig, ax = plt.subplots(figsize=(6,6))
sns.heatmap(
    cmatrix, annot=True, fmt='.3f',
    vmin=0, vmax=1,
    ax = ax,
    cmap=sns.cubehelix_palette(start=.7, rot=-.7, as_cmap=True)
)
ticks = list(map(lambda x: map_id2cultivo[map_le2id[x]], [int(l._text) for l in ax.get_xticklabels()]))
ax.set_yticklabels(ticks, rotation=45)
ax.set_xticklabels(ticks, rotation=45, ha='right', rotation_mode='anchor')
plt.suptitle(f'Matriz de confusión sobre conjunto de validación', fontsize=16)
plt.tight_layout()
plt.savefig('plots/cmatrix_000.png')


hits_misses = (
    pd
    .read_csv('model/hits_misses_000.csv', header=0, names=['Aciertos','Errores','Puntaje'])
)

idx = pd.IndexSlice
idx_row = hits_misses[hits_misses.Aciertos>=2*(hits_misses.Errores+1)].index.to_list()
slice_ = idx[idx_row, hits_misses.columns.to_list()]
min_score_ = idx[idx_row[0], hits_misses.columns.to_list()]
(
    hits_misses
    .style
    .set_properties(**{
        'background-color': 'darkseagreen',
        },
        subset=slice_
    )
    .set_properties(**{
        'border': '3px dashed darkgreen'
        },
        subset=min_score_
    )
    .hide(axis="index")
    .to_latex('plots/tablaPuntajes.tex')
)


train_sqlite_files = glob(f'data/selection_verdad_campo/*.sqlite')
train_data = pd.DataFrame()
for sf in train_sqlite_files:
    file_name = os.path.basename(sf)
    tile = re.search(r'\d+',file_name).group()
    cnx = connect(sf)
    df = pd.read_sql_query("SELECT * FROM output", cnx)
    df['tile_file'] = tile
    train_data = pd.concat([train_data, df], ignore_index=True)


deptos_sqlite_files = glob(f'data/selection_departamentos/*.sqlite')
deptos_data = pd.DataFrame()
for sf in deptos_sqlite_files:
    file_name = os.path.basename(sf)
    tile = re.search(r'\d+',file_name).group()
    cnx = connect(sf)
    df = pd.read_sql_query("SELECT * FROM output", cnx)
    df['tile_file'] = tile
    deptos_data = pd.concat([deptos_data, df], ignore_index=True)


merge_data = (
    train_data
    .merge(deptos_data[['nombre','ogc_fid','tile_file']], how='left',on=['ogc_fid','tile_file'], indicator=True)
)

merge_data.groupby(['nombre','cultivo'], as_index=False).size()

report = pd.read_json('model/report_000.json')
report.drop(columns=['accuracy'], inplace=True)

def map_column(col:str):
    try:
        le = int(col)
        id = map_le2id.get(le, le)
        cultivo = map_id2cultivo.get(id, id)
        return cultivo.title()
    except:
        return col.title()

report.rename(columns={c:map_column(c) for c in report.columns}, inplace=True)
report.to_latex('plots/report.tex')
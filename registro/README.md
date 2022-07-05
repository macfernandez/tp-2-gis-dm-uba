# Hoja de ruta

Se descargaron imágenes del suelo y se dividieron en dos partes o _tiles_
(`~00000.tif` y `~12544.tif`). Cada uno cuenta con 7 bandas (ver [README.md](../README.md)). Las imágenes
corresponden a 6 días distintos (01-10-2020, 01-11-2020,
01-12-2020, 01-01-2021, 20-02-2021, 17-03-2021).

Además, contamos con un archivo `.shp` con la verdad de
campo, etiquetada con los cultivos de la zona.

## Cultivos del suelo

Cotejo qué cultivos fueron indicados en mi archivo de verdad de campo:

```
ogrinfo -sql "SELECT DISTINCT cultivo FROM verdad_campo" data/verdad_campo/verdad_campo.shp
```

Salida (guardada en [verdad_campo_cultivos.txt](verdad_campo_cultivos.txt)):

```
INFO: Open of `data/verdad_campo/verdad_campo.shp'
      using driver `ESRI Shapefile' successful.

Layer name: verdad_campo
Geometry: None
Feature Count: 5
Layer SRS WKT:
(unknown)
cultivo: String (10.0)

OGRFeature(verdad_campo):0
  cultivo (String) = MAIZ

OGRFeature(verdad_campo):1
  cultivo (String) = SOJA

OGRFeature(verdad_campo):2
  cultivo (String) = GIRASOL

OGRFeature(verdad_campo):3
  cultivo (String) = CAMPONATUR

OGRFeature(verdad_campo):4
  cultivo (String) = ALFALFA
```

## Cálculo de índices

Tomo los archivos de cada _tile_ `~00000.tif` y `~12544.tif` de cada período y calculo el
NDVI y el NDSI.

```
python -m src.indexes images -i NDVI NDSI
```

## Concatenación de índices

Concateno cada índice de cada período en un único archivo `.tif`:

```
python -m src.concat_images -i NDVI NDSI -o data/ images
```

Luego, concateno los archivos de todos los índices

```
bash -c 'source ~/OTB-8.0.1-Linux64/otbenv.profile;\
otbcli_ConcatenateImages \
-il results/00000_ndvi.tif results/00000_ndsi.tif \
-out data/concat/00000_concated.tif -ram 500'
```

```
bash -c 'source ~/OTB-8.0.1-Linux64/otbenv.profile;\
otbcli_ConcatenateImages \
-il results/12544_ndvi.tif results/12544_ndsi.tif \
-out data/concat/12544_concated.tif -ram 500'
```

## Selección de pixeles para entrenamiento

Para cada _tile_, obtengo las estadísticas resumidas con
`PolygonClassStatistics`. Eso genera un archivo `.xml.`
con la cantidad de pixeles que hay en cada clase.

Con `SampleSelection` selecciono qué pixeles de cada clase voy a usar para
entrenar. Eso devuelve un archivo `.sqlite`. Ahí, cada pixel es un punto de
las posiciones.

Con `SampleExtraction` extraigo los pixeles seleccionados previamente.

```
python -m src.workflow concat_folder verdad_campo/verdad_campo.shp [--ram]
```

- `concat_folder`: carpeta donde se encuentran los archivos concatenados.
Debe tener solo esos archivos. Si los _tiles_ ya fueron _mergeados_, tendrá
un solo archivo de todo el territorio y, si no, tendrá dos archivos, uno por
cada _tile_.
- `vec_shp`: path al archivo `.shp` con el que se reccortará la imagen.
- `ram`: opcionalmente, se puede indicar la RAM a usar en todos los comandos.
Por defecto utiliza 1Gb.

## Entrenamiento - Iteración #01

Entreno una Regresión Logística básica con la verdad de campo y
hago las predicciones sobre el dataset completo:

```
python -m src.randomforest_iter_01 sqlite-folder tif-folder
```

- sqlite-folder: carpeta con archivos `.sqlite` para armar conjunto de entrenamiento.
- tif-folder: carpeta con archivos `.tif` para armar conjunto de predicción.

Si los _tiles_ ya fueron _mergeados_, dichas carpetas deberían tener un solo archivo
que reúna los pixeles de los dos _tiles_. Si todavía no se realizó el _mergeo_, cada
carpeta contendrá dos archivos, uno por _tile_.

Esto también puede verse en [esta notebook](../nb/modelo_sklearn.ipynb).
## [TO-DO] Análisis - Iteración #01

Analizar las probabilidades predichas en el apartado anterior y definir un punto de
corte.
Evaluar si conviene o no recortar variables (esto se podría analizar considerando los
coeficientes, quizás).

## Levantar dataset de test a Python

Buscamos poder levantar el (o los) _tile(s)_ con todas las bandas
a Python a fin de tenerlos como _dataframe_ y facilitar las iteraciones
de los modelos. Inspirándonos en los pasos del `src.workflow`,
necesitamos una capa `.shp` que abarque toda la zona de estudio y
reemplace a `verdad_campo.shp`. Esto generaría un `.sqlite` con todos
los pixeles del _tile_. Sin embargo, no es necesario levantar todo el
_tile_, solamente el área cultivable. Por eso, usamos la máscara
compartida por Bayle que delimita las zonas cultivables. Por lo que,
en primer lugar, se descarga la máscara:

```
gsutil -m cp gs://gis2022-teledeteccion/clase12/mask/mask_agri_aoi.tif data/
```

Siendo que esta máscara es un raster cuyos valores son `1` o `NaN`
(siendo `1 = área cultivable`), es necesario vectorizarlo, obteniendo
un archivo `.shp` con polígonos cuyo único atributo tendrá el valor `1`.

```
gdal_polygonize.py mask_agri_aoi.tif mask_agri_aoi.shp
```

Los pasos siguientes son repetir el `src.workflow` reemplazando
`verdad_campo.shp` por `mask_agri_aoi.shp`.

```
python -m src.workflow concat_folder mask_agri_aoi.shp [--ram]
```

Se obtiene el `.sqlite` que abarca toda la zona cultivable, con
la etiqueta `1`.

## [TO-DO] Realizar el etiquetado continuo

## [TO-DO] Análisis de cómo se fue modificando la verdad de campo en las iteraciones

## [TO-DO] Rehacer los pasos de la bitácora con la nueva verdad de campo

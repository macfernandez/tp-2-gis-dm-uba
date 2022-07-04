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
-out results/00000_concated.tif -ram 500'
```

```
bash -c 'source ~/OTB-8.0.1-Linux64/otbenv.profile;\
otbcli_ConcatenateImages \
-il results/12544_ndvi.tif results/12544_ndsi.tif \
-out results/12544_concated.tif -ram 500'
```

## Selección de pixeles para entrenamiento

Para cada _tile_, obtengo las estadísticas resumidas con
`PolygonClassStatistics`. Eso genera un archivo `.xml.`
con la cantidad de pixeles que hay en cada clase.

```
python -m src.workflow PolygonClassStatistics \
data/concat/00000_concated.tif \
data/verdad_campo/verdad_campo.shp \
id \
data/polygonclass/00000_classes_stats.xml
1000
```

```
python -m src.workflow PolygonClassStatistics \
data/concat/12544_concated.tif \
data/verdad_campo/verdad_campo.shp \
id \
data/polygonclass/12544_classes_stats.xml
1000
```

Con `SampleSelection` selecciono qué pixeles de cada clase voy a usar para
entrenar. Eso devuelve un archivo `.sqlite`. Ahí, cada pixel es un punto de
las posiciones.

```
python -m src.workflow SampleSelection \
data/concat/00000_concated.tif \
data/verdad_campo/verdad_campo.shp \
data/polygonclass/00000_classes_stats.xml \
id \
total \
data/selection/00000_rates.csv \
data/selection/00000_samples.sqlite \
1000
```

```
python -m src.workflow SampleSelection \
data/concat/12544_concated.tif \
data/verdad_campo/verdad_campo.shp \
data/polygonclass/12544_classes_stats.xml \
id \
total \
data/selection/12544_rates.csv \
data/selection/12544_samples.sqlite \
1000
```

Con `SampleExtraction` extraigo los pixeles seleccionados previamente.

```
python -m src.workflow SampleExtraction \
data/concat/00000_concated.tif \
data/selection/00000_samples.sqlite \
id 1000
```

```
python -m src.workflow SampleExtraction \
data/concat/12544_concated.tif \
data/selection/12544_samples.sqlite \
id 1000
```

## Entrenamiento

Entreno una Regresión Logística básica con la verdad de campo y
hago las predicciones sobre el dataset completo:

```
python -m src.rl_iter_01 sqlite-folder tif-folder
```

- sqlite-folder: 
- tif-folder:
# Hoja de ruta

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

Tomo los archivos `~00000.tif` y `~12544.tif` de cada período y calculo el
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
-out results/00000_concated.tiff -ram 500'
```

```
bash -c 'source ~/OTB-8.0.1-Linux64/otbenv.profile;\
otbcli_ConcatenateImages \
-il data/12544_ndvi.tif data/12544_ndsi.tif \
-out data/12544_concated.tiff -ram 500'
```

## Unión de los _raster_

Uno los _rasters_ concatenados para tener una única imagen del terreno:

```
gdal_merge.py -ot UInt32 -o data/merge_tmp.tif \
    data/00000_concated.tif data/12544_concated.tif
```

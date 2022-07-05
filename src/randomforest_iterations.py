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
python -m src.workflow concat_folder mask_agri_aoi [--ram]
```

Se obtiene el `.sqlite` que abarca toda la zona cultivable, con
la etiqueta `1`.
# Uso de scriptss

Los programas en esta carpeta deben invocarse desde el _root_ del repositorio
(en `~/tp-2-gis-dm-uba`).

## indexes.py

```
python -m src.indexes input_folder [-i] [-b]
```

- `input_folder`: carpeta que contiene subcarpetas con archivos `.tif`.
- `-i`, `--index` (opcional): índices que se desean calcular. Puede ser cualquiera de los definidos en el archivo [indexes_definition.py](./indexes_definition.py)y puede indicarse más de uno. Si no se indica ninguno, calcula todos.
- `-b`, `--bucket` (opcional): URI al bucket y carpeta donde se quiere guardar la capa generada. Ejemplo: `gs://my-bucket/folder/`. Si se indica un bucket, no se guarda en local. Si no se lo indica, la capa se guarda en local en la misma carpeta `input_folder` con un sufijo que indica el índica calculado.

Ejemplos:

Calcula los índices NDVI y NDSI y los guarda en el bucket indicado.

```
python -m src.indexes my-path -i NDVI NDSI -b gs://bucket/folder
```

Calcula todos los índices y los guarda localmente.
```
python -m src.indexes my-path
```

## concat_images.py

```
python -m src.concat_images input_folder [-t] [-o] [-i] [-b]
```

- `input_folder`: carpeta que contiene subcarpetas con archivos `.tif`.
- `-t`, `--tile` (opcional): últimos cindo (5) dígitos del tile de las capas a unit (00000 o 12544)
- `-o`, `--output-folder` (opcional): carpeta para guardar la concatenación. Si no se indica ninguna, se guardan en `results`. Si la carpeta indicada no existe, la crea.
- `-i`, `--index` (opcional): índices cuyas capas se quieran concatenar. Puede ser cualquiera de los definidos en el archivo [indexes_definition.py](./indexes_definition.py) y puede indicarse más de uno. Si no se indica ninguno, intenta concatenar todos. WARNING: deben indicarse solamente índices cuyas capas hayan sido calculadas previamente.
- `-b`, `--bucket` (opcional): URI al bucket y carpeta donde se quiere guardar la capa generada. Ejemplo: `gs://my-bucket/folder/`. Si se indica un bucket, no se guarda en local.

# Índices espectrales

Definición de las fórmulas de índices espectrales.

## Fórmulas
### NDVI: Normalized Difference Vegetation Index

$$
NDVI = \frac{NIR-RED}{NIR+RED}
$$

### NDVI A:

$$
\text{NDVI A} = \frac{\text{RED EDGE 4}-RED}{\text{RED EDGE 4}+RED}
$$

### NDSI: Normalized Difference Snow Index

$$
NDSI = \frac{GREEN-\text{SWIR 1}}{GREEN+\text{SWIR 1}}
$$

### NBI: Normalized Burn Ratio

$$
NBI = \frac{NIR-\text{SWIR 2}}{NIR+\text{SWIR 2}}
$$

### NDWI: Normalized Difference Water Index (Gao, 1996)

$$
NDWI = \frac{NIR-\text{SWIR 1}}{NIR+\text{SWIR 1}}
$$

### NDWI: Normalized Difference Water Index (McFeeters, 1996)

$$
NDWI = \frac{GREEN-NIR}{GREEN+NIR}
$$

## Traducción de a las bandas de la capa

| Sentinel | Descripción | En nuestra capa |
|:---------|:------------|:----------------|
| B2       | Blue        | Banda 1         |
| B3       | Green       | Banda 2         |
| B4       | Red         | Banda 3         |
| B8       | NIR         | Banda 4         |
| B8A      | Red Edge 4  | Banda 5         |
| B11      | SWIR 1      | Banda 6         |
| B12      | SWIR 2      | Banda 7         |

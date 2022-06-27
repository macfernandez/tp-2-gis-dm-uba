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

### NGRDI: Normalized Green–Red Difference Index (Hunt, 2005)

$$
NGRDI = \frac{GREEN-RED}{GREEN+RED}
$$

### TGI: Triangular Greenness Index (Hunt, 2012)

$$
TGI = -0.5 \times [190 \times (RED - GREEN) - 120 \times (RED - BLUE)]
$$

### CVI: Chlorophyll Vegetation Index (Vincini, 2008)

$$
CVI = \frac{\frac{NIR}{GREEN}}{\frac{GREEN}{RED}}
$$

### AFRI 1.6: Aerosol free vegetation index 1.6 (Karineli, 2001)

$$
AFRI\_1\_6 = \frac{\text{RED EDGE 4}-0.66 \times \text{SWIR 1}}{\text{RED EDGE 4}+0.66 \times \text{SWIR 1}}
$$

### AFRI 2.1: Aerosol free vegetation index 2.1 (Karineli, 2001)

$$
AFRI\_2\_1 = \frac{\text{RED EDGE 4}-0.5 \times \text{SWIR 2}}{\text{RED EDGE 4}+0.5 \times \text{SWIR 2}}
$$

### ARVI: Atmospherically resistant vegetation index (Kaufman, 1992)

$$
ARVI = \frac{NIR-2 \times GREEN+Blue}{NIR+2 \times GREEN-Blue}
$$

### ARVI 2: Atmospherically resistant vegetation index 2 (Kaufman, 1992)

$$
ARVI\_2 = -0.18 + 1.17 \times \frac{NIR-RED}{NIR+RED}
$$

### ATSAVI: Adjusted Transformed Soil-Adjusted Vegetation Index (BARET, 1991)

$$
ATSAVI = \frac{1.22 \times (NIR-1.22 \times RED-0.03)}{NIR+RED+0.162472}
$$

### AVI: Ashburn Vegetation Index (Ashburn, 1978)

$$
AVI = 2 \times \text{RED EDGE 4}-RED
$$

### BNDVI: Blue-Normalized Difference Vegetation Index (Yang, 2007)

$$
BNDVI = \frac{NIR-Blue}{NIR+Blue}
$$

### CRI 550: Carotenoid Reflectance Index 550 (Gitelson, 2001)

$$
CRI\_550 = \frac{1}{Blue}-\frac{1}{GREEN}
$$

### EPIChlb: Eucalyptus Pigment Index for Chlorophyll b (Datt, 1997)

$$
EPIChlb = 0.0337 \times (\frac{RED}{GREEN})^2
$$

### EVI 2: Enhanced Vegetation Index 2 (Miura, 2008)

$$
EVI\_2 = 2.4 \times \frac{NIR-RED}{NIR+RED+1}
$$

### GARI: Green Atmospherically Resistant Vegetation Index (Gitelson, 1996)

$$
GARI = \frac{NIR-(GREEN-(BLUE-RED))}{NIR-(GREEN+(BLUE-RED))}
$$

### GBNDVI: Green-Blue Normalized Difference Vegetation Index (Wang, 2010)

$$
GBNDVI = \frac{NIR-(GREEN+BLUE)}{NIR+(GREEN+BLUE)}
$$

### GNDVI: Green Normalized Difference Vegetation Index (Gitelson, 1996)

$$
GNDVI = \frac{NIR-GREEN}{NIR+GREEN}
$$

### GVMI: Global Vegetation Moisture Index (Glenn, 2010)

$$
GVMI = \frac{NIR+0.1-(\text{SWIR 2}+0.02)}{NIR+0.1+(\text{SWIR 2}+0.02)}
$$

### MCARI 1: Modified Chlorophyll Absorption in Reflectance Index (Daughtry, 2000)

$$
MCARI\_1 = 1.2 \times [2.5 \times (NIR-RED)-1.3 \times (NIR-GREEN)]
$$

### mNDVI: Modified Normalized Difference Vegetation Index (Main, 2001)

$$
mNDVI = \frac{NIR-RED}{NIR+RED-2 \times BLUE}
$$

### MSAVI 2: Modified Soil-Adjusted Vegetation Index 2 (Qi, 1994)

$$
MSAVI\_2 = \frac{2 \times NIR+1-\sqrt{(2 \times NIR+1)^2-8 \times (NIR-RED)}}{2}
$$

### MSR 670: Modified Simple Ratio 670/800 (Chen, 1996)

$$
MSR\_670 = \frac{\frac{NIR}{RED}-1}{\sqrt{\frac{NIR}{RED}-1}}
$$

### MTVI 2: Modified Triangular Vegetation Index 2 (Haboudane, 2004)

$$
MTVI\_2 = 1.5 \times \frac{1.2 \times (NIR-GREEN)-2.5 \times (RED-GREEN)}{\sqrt{2 \times (NIR+1)^2-(6 \times NIR -5 \times \sqrt{RED})-0.5}}
$$

### NBR: Normalized difference NIR/SWIR normalized Burn Ratio (Key, 2005)

$$
NBR = \frac{NIR-\text{SWIR 2}}{NIR+\text{SWIR 2}}
$$

### NDII: Normalized Difference Infrared Index (Hardisky, 1983)

$$
NDII = \frac{NIR-\text{SWIR 1}}{NIR+\text{SWIR 1}}
$$

### RBNDVI: Red–Blue Normalized Difference Vegetation Index (Wang, 2007)

$$
RBNDVI = \frac{NIR-(RED-BLUE)}{NIR+(RED-BLUE)}
$$

### SIPI: Structure Intensive Pigment Index (Penuelas, 1995)

$$
SIPI = \frac{NIR-BLUE}{NIR-RED}
$$

### SIWSI: Shortwave Infrared Water Stress Index (Fensholt, 2010)

$$
SIWSI = \frac{\text{RED EDGE 4}-\text{SWIR 1}}{\text{RED EDGE 4}+\text{SWIR 1}}
$$

### SLAVI: Shortwave Infrared Water Stress Index (Fensholt, 2010)

$$
SIWSI = \frac{NIR}{RED+\text{SWIR 2}}
$$

### VARIgreen: Visible Atmospherically Resistant Index Green (Gitelson, 2001)

$$
VARI\_green = \frac{GREEN-RED}{GREEN-RED+BLUE}
$$

### WDRVI: Normalized Difference Vegetation Index

$$
NDVI = \frac{0.1 \times NIR-RED}{0.1 \times NIR+RED}
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


## Bibliografía:
1. NGDRI-TGI-CVI: https://www.mdpi.com/2073-4395/10/5/641
2. Todos índices siguientes a CVI: https://www.spiedigitallibrary.org/journals/journal-of-applied-remote-sensing/volume-12/issue-2/026019/Crop-classification-from-Sentinel-2-derived-vegetation-indices-using-ensemble/10.1117/1.JRS.12.026019.full?SSO=1

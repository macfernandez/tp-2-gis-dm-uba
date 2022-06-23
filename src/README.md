# Índices espectrales

Definición de las fórmulas de índices espectrales.

## Fórmulas
### NDVI: Normalized Difference Vegetation Index

$$
NDVI = \frac{NIR-RED}{NIR+RED}
$$

### NDVI: Normalized Difference Vegetation Index

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
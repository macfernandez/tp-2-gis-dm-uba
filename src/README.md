# Índices espectrales

Definición de las fórmulas de índices espectrales.

## Fórmulas
### NDVI: Normalized Difference Vegetation Index

$$
NDVI = \frac{NIR-RED}{NIR+RED}
$$

### NDSI: Normalized Difference Snow Index

$$
NDSI = \frac{GREEN-SWIR2}{GREEN+SWIR2}
$$

### NBI: Normalized Burn Ratio

$$
NBI = \frac{NIR-SWIR2}{NIR+SWIR2}
$$

### NDWI: Normalized Difference Water Index (Gao, 1996)

$$
NDWI = \frac{NIR-SWIR 1}{NIR+SWIR 1}
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
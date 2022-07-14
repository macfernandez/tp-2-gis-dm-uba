## shp de deptos a raster

library(sf)
library(raster)
library(tidyverse)
library(data.table)

deptos <- st_read("data/departamentos/departamentos.shp")

as.factor(deptos$nombre) %>%
  levels
deptos$idnombre <- as.numeric(as.factor(deptos$nombre))

codigo <- deptos[, c("nombre", "idnombre")] %>%
  st_drop_geometry()

fwrite(codigo, "data/departamentos/codigo.csv")

deptos <- deptos[, c("idnombre")]
names(deptos)[1] <- "id"

r.chico <- merge(raster("data/00000.tif"), raster("data/12544.tif"))

library(fasterize)

deptos.raster <- fasterize(sf=deptos, raster=r.chico, field="id")

writeRaster(deptos.raster, "data/raster_deptos", format = "GTiff")


fasterize(sf=deptos, raster=raster("data/00000.tif"), field="id") %>%
  writeRaster("data/raster_00000_deptos", format = "GTiff")


fasterize(sf=deptos, raster=raster("data/12544.tif"), field="id") %>%
  writeRaster("data/raster_12544_deptos", format = "GTiff")

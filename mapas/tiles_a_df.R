# importancia a csv:
library(sf)
library(raster)
library(tidyverse)
library(data.table)


#Levanto los datos

r.000 <- stack("data/importance_00000.tif")
names(r.000) <- paste0("band_", 0:27)
nvc.000 <- raster("data/00000.tif")
names(nvc.000) <- "cultivo"
deptos.000 <- raster("data/raster_00000_deptos.tif")
names(deptos.000) <- "depto"
r.000 <- addLayer(r.000, nvc.000, deptos.000)
rm(nvc.000)

r.125 <- stack("data/importance_12544.tif")
names(r.125) <- paste0("band_", 0:27)
nvc.125 <- raster("data/12544.tif")
names(nvc.125) <- "cultivo"
deptos.125 <- raster("data/raster_12544_deptos.tif")
names(deptos.125) <- "depto"
r.125 <- addLayer(r.125, nvc.125, deptos.125)
rm(nvc.125)



r.000 <- as.data.frame(r.000, xy = TRUE)
setDT(r.000)
r.000[, tile := 00000]
r.125 <- as.data.frame(r.125, xy = TRUE)
setDT(r.125)
r.125[, tile := 12544]

r.000 <- r.000[!is.na(band_1)]
r.125 <- r.125[!is.na(band_1)]

gc()

r <- rbind(r.000, r.125)

rm(r.000, r.125)

gc()

#Lo guardo
fwrite(r, "data/00000_12544_nvc.csv")

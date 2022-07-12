
library(tidyverse)
library(sf)
library(ggspatial)
library(ggthemes)
library(wesanderson)
library(data.table)
library(raster)


carpeta <- c("../../datos-gis/")
archivos <- list.files(carpeta, full.names = TRUE)
archivos <- archivos[grepl(".tif", archivos)]

for(i in archivos){
  if(which(i == archivos) == 1){
    r <- raster(i)
  }else{
    r <- merge(r, raster(i))
  }
}

sum(is.na(r[]))
sum(r[] == -99)

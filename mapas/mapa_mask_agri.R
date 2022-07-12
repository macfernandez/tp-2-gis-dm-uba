# Mapa de mask agri:

library(dplyr)
library(tidyverse)
library(sf)
library(ggspatial)
library(ggthemes)
library(wesanderson)
library(data.table)
library(raster)

Sys.setenv(LANG = "es")

deptos <- st_read("mapas/data/departamentos/departamentos.shp")%>%
  mutate(nombre = str_to_title(nombre))

mascara <- raster("mapas/data/mask_agri/mask_agri_aoi.tif")

paleta <- wes_palette("Darjeeling1", n = uniqueN(mascara[1:10,1:10]))

unique(mascara[])

mascar_spdf <- as(mascara, "SpatialPixelsDataFrame")
mascara_df <- as.data.frame(mascara_spdf)
colnames(mascara_df) <- c("value", "x", "y")

ggplot() +
  geom_raster(data = mascara_df, aes(x = x, y = y, fill = as.factor(value))) +
  geom_sf(data = deptos) +
  coord_sf(label_axes = "ENEN") +
  theme_bw() +
  annotation_scale(
    location = "br",
    bar_cols = c("grey60", "white")) +
  annotation_north_arrow(
    location = "tr", which_north = "true",
    pad_x = unit(0.4, "in"), pad_y = unit(0.4, "in"),
    style = north_arrow_fancy_orienteering()) +
  scale_x_continuous(labels = function(x) paste0(abs(x), "°O")) +
  scale_fill_manual(values = paleta) +
  labs(fill = str_wrap("Municipios/Partido de la zona de estudio", 25))+
  theme(axis.title = element_blank())
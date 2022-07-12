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

paleta <- wes_palette("Darjeeling1", n = 2)

unique(mascara[])

mascar_spdf <- as(mascara, "SpatialPixelsDataFrame")
mascara_df <- as.data.frame(mascar_spdf)
colnames(mascara_df) <- c("value", "x", "y")

mapa_mask_agri <- ggplot() +
  geom_raster(data = mascara_df, aes(x = x, y = y, fill = as.factor(value))) +
  geom_sf(data = deptos, fill = "transparent") +
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
  scale_fill_manual(values = paleta, label = c("No cultivable", "Cultivable")) +
  labs(fill = "Tipo de área")+
  theme(axis.title = element_blank())

ggsave("mapas/figuras/mapa_mask_agri.png", mapa_mask_agri, width = 8, heigh = 8)


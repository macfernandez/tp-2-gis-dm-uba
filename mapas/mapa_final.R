# Mapa estimaciones finales

rm(list = ls())

library(tidyverse)
library(sf)
library(ggspatial)
library(ggthemes)
library(wesanderson)
library(data.table)
library(raster)
library(ggsci)


deptos <- st_read("data/departamentos/departamentos.shp")%>%
  mutate(nombre = str_to_title(nombre))


r <- raster("data/results_merge_mask.tif")

r_df <- as(r, "SpatialPixelsDataFrame")
r_df <- as.data.table(r_df)
colnames(r_df) <- c("value", "x", "y")

r_df <- r_df[value > 0]

r_df[, value := fcase(value %in% c(1, 4), "Soja",
                      value %in% c(2, 3), "Maíz",
                      value == 5, "Girasol",
                      value == 10, "Alfalfa",
                      value == 20, "Campo Natural")]

paleta <- wes_palette("Cavalcanti1", n = 5)


mapa_nvc <- ggplot() +
  geom_raster(data = r_df, aes(x = x, y = y, fill = value)) +
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
  #scale_fill_nejm() +
  scale_fill_manual(values = paleta) +
  labs(fill = "Clasificación de cultivos")+
  theme(axis.title = element_blank())

ggsave("figuras/mapa_final.png", mapa_nvc, width = 8, heigh = 6)

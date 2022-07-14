#Mapa verdad campo
rm(list=ls())
gc()

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

r <- raster("data/merge_nvc.tif")

r[][r[] == -111] <- NA

r[][!is.na(r[])] <- 0


#Presencia/ausencia de puntos sobre raster
verdad <- st_read("data/verdad_campo/verdad_campo.shp")
points_to_raster <- rasterize(x=verdad, y=r, field=1)

points_to_raster[][is.na(points_to_raster[])] <- 0

r[] <- r[] + points_to_raster[]

r_df <- as(r, "SpatialPixelsDataFrame")
r_df <- as.data.table(r_df)
colnames(r_df) <- c("value", "x", "y")

r_df <- r_df[!is.na(value)]
r_df[, value := fifelse(value == 0, "No", "Sí")]

paleta <- wes_palette("Cavalcanti1", n = 2)

mapa_verdad <- ggplot() +
  geom_raster(data = r_df, aes(x = x, y = y, fill = as.factor(value))) +
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
  scale_fill_manual(values = paleta) +
  labs(fill = str_wrap("Clasificado como nueva verdad de campo", 20))+
  theme(axis.title = element_blank())

ggsave("figuras/mapa_verdad_campo.png", mapa_verdad, width = 8, heigh = 6)

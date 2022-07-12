# Mapa de departamentos:

#library(tmap)
library(dplyr)
library(tidyverse)
library(sf)
library(ggspatial)
library(ggthemes)
library(wesanderson)
library(data.table)

Sys.setenv(LANG = "es")

#setwd("..")

deptos <- st_read("mapas/data/departamentos/departamentos.shp")%>%
  mutate(nombre = str_to_title(nombre))
provincias <- st_read("mapas/data/provincias/provincias.shp")

paleta <- wes_palette("Darjeeling1", n = uniqueN(deptos$nombre))

mapa.deptos <- ggplot(provincias) +
  geom_sf() +
  geom_sf(data = deptos, aes(fill = nombre)) +
  geom_sf_text(aes(label = ifelse(grepl("iudad", NAM), NA, NAM)), size = 2) +
  coord_sf(label_axes = "ENEN") +
  theme_bw() +
  scale_y_continuous(sec.axis = dup_axis()) +
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

ggsave("mapas/figuras/mapa_deptos.png", mapa.deptos, width = 8, heigh = 8)


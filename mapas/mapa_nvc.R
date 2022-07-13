
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

carpeta <- c("data/")
archivos <- list.files(carpeta, full.names = TRUE)
archivos <- archivos[grepl(".tif", archivos)]

for(i in archivos){
  if(which(i == archivos) == 1){
    r <- raster(i)
  }else{
    r <- merge(r, raster(i))
  }
}

writeRaster(r, "data/merge_nvc", format = "GTiff")

r_df <- as(r, "SpatialPixelsDataFrame")
r_df <- as.data.table(r_df)
colnames(r_df) <- c("value", "x", "y")

r_df[value == -111, "value"] <- NA_integer_

r_df[, value := as.factor(value)]

paleta <- wes_palette("Cavalcanti1", n = 2)



mapa_nvc <- ggplot() +
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
  scale_fill_nejm(label = c("", "No cultivable", "Cultivable")) +
  labs(fill = str_wrap("Clasificación de la nueva verdad de campo", 20))+
  theme(axis.title = element_blank())

ggsave("figuras/mapa_nvc.png", mapa_nvc, width = 8, heigh = 7)


r_df[, value := fifelse(value == "-99", "No", "Sí")]

r_df <- r_df[!is.na(value)]


mapa_nvc_dic <- ggplot() +
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
  scale_fill_manual(values = paleta,label = c("", "No cultivable", "Cultivable")) +
  labs(fill = str_wrap("Clasificación como nueva verdad de campo", 20))+
  theme(axis.title = element_blank())

ggsave("figuras/mapa_nvc_dic.png", mapa_nvc_dic, width = 8, heigh = 7)

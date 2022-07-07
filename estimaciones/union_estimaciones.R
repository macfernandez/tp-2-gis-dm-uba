library(tidyverse)
library(dplyr)

estimaciones <- list.files("estimaciones/originales/", full.names = TRUE)
estimaciones <- rbindlist(lapply(estimaciones, fread, select = c("Cultivo", "Departamento", "Sup. Sembrada")))
estimaciones <- estimaciones[, .(cultivo = Cultivo, nombre = Departamento, ha = `Sup. Sembrada`)]
estimaciones[, c("nombre", "cultivo") := .(gsub("PRESIDENTE", "PTE", nombre),
                                           gsub(" total", "", cultivo) %>%
                                             toupper)]

fwrite(estimaciones, "estimaciones/estimaciones_inta.csv")
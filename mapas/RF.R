#Entrenamiento con RF:

library(tidyverse)
library(data.table)
library(lightgbm)

train <- fread("data/00000_12544_nvc.csv")

train <- as.matrix(train[cultivo > 0, -c("x", "y", "tile", "depto")])

cultivos <- unique(train[, col.puntaje])

id.cultivo <- 0:6

codigo.cultivo <- data.table(cultivos = cultivos[order(cultivos)], id.cultivo)

fwrite(codigo.cultivo, "data/codigo_cultivo.csv")

train[, col.puntaje] <- as.numeric(as.factor(train[, col.puntaje]))-1

col.puntaje <- which(colnames(train) == "cultivo")

dtrain <- lgb.Dataset(
  data = train[, -col.puntaje]
  , label = train[, col.puntaje]
)

mejor.params <- list(
  objective = "multiclass",
  num_class = 7,
  seed = 20220707,
  n_estimators = 500,
  max_depth = 10,
  bagging_fraction = sqrt(28)/28,
  metric = "auc_mu",
  min_data_in_leaf = 1,
  feature_fraction = 0.001
)

model <- lightgbm(
  params = mejor.params
  , data = dtrain
)


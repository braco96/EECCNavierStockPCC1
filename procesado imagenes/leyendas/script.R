library(png)  # Para manejar imágenes PNG
library(grid) # Para visualizar imágenes

# Definir la función
extraer_y_guardar_por_bloques <- function(image_path, output_dir) {
  # Verificar si el archivo existe
  if (!file.exists(image_path)) {
    stop("El archivo no existe en la ruta especificada.")
  }
  
  # Cargar la imagen
  image <- readPNG(image_path)
  
  # Verificar dimensiones de la imagen
  if (length(dim(image)) < 2) {
    stop("La imagen cargada no tiene las dimensiones esperadas.")
  }
  
  # Dimensiones de la imagen
  height <- dim(image)[1]  # Altura
  width <- dim(image)[2]   # Ancho
  channels <- ifelse(length(dim(image)) == 3, dim(image)[3], 1)
  
  # Verificar el número de canales y convertir si es necesario
  if (channels == 1) {
    # Convertir escala de grises a RGB
    image <- array(rep(image, 3), dim = c(height, width, 3))
  }
  
  # Crear una carpeta de salida si no existe
  if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
  }
  
  # Inicializar acumulador y contador para los bloques
  bloque_acumulado <- NULL
  bloque_contador <- 1
  
  # Iterar sobre todas las columnas
  for (posicion_columna in 1:width) {
    # Extraer la columna deseada como tira de píxeles
    tira_pixeles <- image[, posicion_columna, ]
    
    # Verificar dimensiones de la tira
    if (length(tira_pixeles) != height * 3) {
      tira_pixeles <- array(rep(tira_pixeles, 3), dim = c(height, 3))
    }
    
    # Filtrar píxeles blancos (R = 1, G = 1, B = 1)
    # Un píxel blanco tiene todos los valores en 1
    es_blanca <- all(tira_pixeles[, 1] == 1 & tira_pixeles[, 2] == 1 & tira_pixeles[, 3] == 1)
    
    if (es_blanca) {
      # Si encontramos una columna blanca, guardar la imagen acumulada actual
      if (!is.null(bloque_acumulado)) {
        output_path <- file.path(output_dir, paste0("bloque_", bloque_contador, ".png"))
        writePNG(bloque_acumulado, output_path)
        cat("Bloque", bloque_contador, "guardado en:", output_path, "\n")
        bloque_contador <- bloque_contador + 1
        bloque_acumulado <- NULL  # Reiniciar acumulador
      }
      next
    }
    
    # Agregar columna no blanca al bloque acumulado
    columna_formada <- array(tira_pixeles, dim = c(height, 1, 3))
    if (is.null(bloque_acumulado)) {
      bloque_acumulado <- columna_formada  # Inicializar acumulador con la primera columna válida
    } else {
      bloque_acumulado <- abind::abind(bloque_acumulado, columna_formada, along = 2)
    }
  }
  
  # Guardar cualquier bloque restante al final
  if (!is.null(bloque_acumulado)) {
    output_path <- file.path(output_dir, paste0("bloque_", bloque_contador, ".png"))
    writePNG(bloque_acumulado, output_path)
    cat("Bloque final", bloque_contador, "guardado en:", output_path, "\n")
  }
}

# Uso de la función
extraer_y_guardar_por_bloques(
  image_path = "F:/edp/valmayor/imagenes/S2A_MSIL1C_20240810T105621_N0511_R094_T30TVK_20240810T130124.SAFE/ant/output/leyendas/dogg.png",
  output_dir = "F:/edp/valmayor/imagenes/S2A_MSIL1C_20240810T105621_N0511_R094_T30TVK_20240810T130124.SAFE/ant/output/leyendas/columnas_por_bloques"
)

# EECCNavierStockPCC1

> 🌊 Proyecto de Trabajo de Fin de Grado (TFG) para el estudio de parámetros de calidad del agua (ej. turbidez, clorofila) en superficies acuáticas. El proyecto automatiza la adquisición y procesamiento de imágenes satelitales (Sentinel-2) para extraer datos que alimentarán simulaciones de ecuaciones (posiblemente Navier-Stokes) en Visual PDE.

---

## 🚩 Índice

* [Descripción del Proyecto](#-descripción-del-proyecto)
* [Flujo de Trabajo (Workflow)](#-flujo-de-trabajo-workflow)
* [Características Principales](#-características-principales)
* [Tecnologías Utilizadas](#-tecnologías-utilizadas)
* [Instalación y Configuración](#-instalación-y-configuración)
* [Modo de Uso](#-modo-de-uso)
* [Estructura de Carpetas (Sugerida)](#-estructura-de-carpetas-sugerida)
* [Pasos Futuros y Mejoras](#-pasos-futuros-y-mejoras)
* [Autor](#-autor)

---

## 📜 Descripción del Proyecto

Este repositorio contiene el código fuente para el TFG `EECCNavierStockPCC1`. El objetivo principal es crear un pipeline automatizado que:

1.  Define un **Área de Interés (AOI)**, como un embalse o lago (ej. cerca de Madrid), a partir de coordenadas UTM o un polígono GeoJSON.
2.  Consulta y descarga imágenes satelitales **Sentinel-2 (MSIL1C)** del Copernicus Data Space Ecosystem.
3.  Utiliza **Docker** para ejecutar el software **ACOLITE**, aplicando correcciones atmosféricas y procesando las imágenes para extraer parámetros de calidad del agua (reflectancia, turbidez, clorofila, etc.).
4.  Prepara los datos extraídos para un análisis posterior de **filtrado de color** (usando scripts en R o MATLAB) y para su carga en **Visual PDE**, donde se utilizarán como parámetros iniciales para simulaciones (posiblemente de dinámica de fluidos).

El proyecto está construido principalmente en **Python** y aprovecha la contenerización de Docker para un procesamiento satelital robusto y reproducible.

---

## 🔄 Flujo de Trabajo (Workflow)

El proceso completo del proyecto sigue estos pasos:

1. **Definición del AOI:** El usuario especifica la zona de estudio mediante coordenadas UTM o polígono GeoJSON.  
2. **Búsqueda de Imágenes:** Consulta la API de Copernicus para obtener imágenes Sentinel-2 con nubosidad <20%.  
3. **Descarga y Descompresión:** Descarga y descomprime automáticamente los productos `.zip` en la carpeta `imagenes/`.  
4. **Procesamiento con ACOLITE:** Genera automáticamente los archivos `settings.txt` y `docker-compose.yml` para cada imagen, ejecutando el contenedor de ACOLITE vía Docker Compose.  
5. **Análisis y Simulación:** Los resultados (GeoTIFFs) se procesan con scripts de R/MATLAB y se importan a Visual PDE para simulaciones posteriores.

---

## ✨ Características Principales

* **Automatización completa del flujo satelital**
* **Definición flexible del AOI (coordenadas o polígono)**
* **Procesamiento reproducible mediante Docker**
* **Extracción de parámetros limnológicos clave**
* **Integración preparada para Visual PDE**
* **Código modular y extensible**

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x  
* **Librerías Python:** `requests`, `pyproj`, `os`, `json`, `zipfile`, `shutil`  
* **Procesamiento Satelital:** Docker + ACOLITE  
* **Plataforma de Datos:** Copernicus Data Space Ecosystem (CDSE)  
* **Análisis Externo:** R, MATLAB, Visual PDE  

---

## 🚀 Instalación y Configuración

1. **Clonar el repositorio:**
    ```bash
    git clone [URL-DEL-REPOSITORIO]
    cd EECCNavierStockPCC1
    ```

2. **Instalar Docker:**
    Asegúrate de tener Docker Desktop (Windows/Mac) o Docker Engine (Linux) en ejecución.

3. **Crear entorno virtual e instalar dependencias:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    echo "requests\npyproj" > requirements.txt
    pip install -r requirements.txt
    ```

---

## ▶️ Modo de Uso

Ejemplo de ejecución:

```python
import datetime

# Definir el área de estudio
poligono_valmayor = [[
    [-4.125147, 40.601409],
    [-4.125147, 40.504992],
    [-3.994625, 40.504992],
    [-3.994625, 40.601409],
    [-4.125147, 40.601409]
]]

fecha_actual = datetime.datetime.now()
fecha_inicio_busqueda = fecha_actual - datetime.timedelta(days=994)

muestra_agua = Muestras(
    utmX=None,
    utmY=None,
    polygono=[poligono_valmayor],
    timeZone=30,
    firstImage=fecha_inicio_busqueda
)
    ```

---

## Ejecuta el script principal:

python main.py


Los resultados procesados (GeoTIFFs) se almacenan en:

imagenes/[NOMBRE_SAFE]/output/
print("Buscando imágenes...")
get_satelite_muestras(muestra_agua)
descargar(muestra_agua)
descomprimir_zips(muestra_agua)
ejecutar_acolite(muestra_agua)

# EECCNavierStockPCC1

Este repositorio contiene scripts y plantillas para descargar imágenes Sentinel-2 desde Copernicus Data Space, procesarlas con [Acolite](https://github.com/acolite/acolite) y posteriormente indexarlas en VisualPDE.

## Descarga de imágenes

El script [`salvador.py`](salvador.py) implementa la lógica necesaria para obtener productos Sentinel-2. La clase `Muestras` define el polígono de interés y construye la consulta a la API de Copernicus, mientras que funciones como `get_access_token`, `descargar` y `download_product` manejan la autenticación y la descarga de los paquetes `.SAFE`【F:salvador.py†L51-L213】.

### Ejemplo de uso
```python
from salvador import Muestras, get_satelite_muestras, descargar, descomprimir_zips

muestra = Muestras(utmX=..., utmY=..., timeZone=..., firstImage=...)
get_satelite_muestras(muestra)
descargar(muestra)
descomprimir_zips(muestra)
```

## Procesado con Acolite

La plantilla [`settings.txt.tpl`](settings.txt.tpl) define los parámetros principales de procesado —por ejemplo `inputfile`, `limit` y las credenciales de EarthData— que serán consumidos por Acolite【F:settings.txt.tpl†L1-L6】.

El archivo [`acolite-docker-compose.yml`](acolite-docker-compose.yml) arranca el contenedor oficial de Acolite y monta las carpetas de entrada y salida para ejecutar el procesado con el fichero de ajustes generado【F:acolite-docker-compose.yml†L1-L7】.

```bash
docker compose -f acolite-docker-compose.yml up
```

## Indexación en VisualPDE

Tras el procesado, los GeoTIFFs y NetCDFs producidos por Acolite pueden indexarse en VisualPDE para su visualización. Este repositorio no contiene el código de indexación, pero los resultados están listos para integrarse en dicha plataforma.

## Estructura del repositorio

- `salvador.py`: descarga de productos Sentinel-2 y preparación de parámetros.
- `acolite-docker-compose.yml`: configuración del contenedor Acolite.
- `settings.txt.tpl`: plantilla de ajustes para el procesado.
- `plantillas/`: versiones base de las plantillas de configuración.

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 14:25:04 2024

@author: Luisbra
"""
from acolite-main import * 
# Objeto con coordenadas de Madrid (aproximadamente)
import datetime
import os
import zipfile
import shutil
import requests
from pyproj import Proj, Transformer
cantidad=3
wgs84_proj = Proj(proj="latlong", datum="WGS84")
distance=1/1000
client_id = 'cdse-public'
username = 'bravocolladoluis@gmail.com'
password = '9YK6XF?@$jbMz_T'
grant_type = 'password'
token_url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
informaciones = []

data = {
    'client_id': client_id,
    'username': username,
    'password': password,
    'grant_type': grant_type
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

COPERNICUS_OPEN_SEARCH_URL = 'https://catalogue.dataspace.copernicus.eu/odata/v1/Products'

class Muestras:
    def __init__(self, utmX, utmY, timeZone, firstImage, lastImage=None):
        self.utmX = utmX
        self.utmY = utmY
        self.timeZone = timeZone
        self.firstImage = firstImage

fecha_actual = datetime.datetime.now()
fecha_hace_14_dias = fecha_actual - datetime.timedelta(days=994)
madrid_muestra = Muestras(utmX=410369, utmY=4488142, timeZone=30, firstImage=fecha_hace_14_dias)
muestra = [madrid_muestra]

utm_proj = Proj(proj="utm", zone=30, ellps="WGS84")
transformer = Transformer.from_proj(utm_proj, wgs84_proj)

def get_access_token() -> str:
    print('satelital :auxiliar_0 Autenticación')
    try:
        response = requests.post(token_url, data=data, headers=headers)
        if response.status_code == 200:
            print('satelital :auxiliar_0 Fin token generado')
            return response.json()['access_token']
        else:
            print(f'Error en la solicitud de token: {response.status_code}')
            raise Exception(f'Error al obtener el token de acceso: {response.status_code}')
    except Exception as error:
        print('satelital :auxiliar_0 Error al obtener el token de acceso:', error)
        raise error

def descargar():
    for info in informaciones[:cantidad]:
        product_url = info[0]  # URL del producto
        product_name = info[1]  # Nombre del producto
        download_product(get_access_token(), product_url, product_name)

# Después de ejecutar la función, modificar 'informaciones'
informaciones = informaciones[:cantidad]


def download_product(access_token: str, product_url: str, name: str) -> None:
    try:
        product_id = product_url.split('/')[-1]
        print('Comenzamos una descarga')
        print('Nombre', name)
        print('Producto', product_id)

        download_path = os.getcwd()  # Directorio actual de trabajo
        output_path = os.path.join(download_path, f'{name}.zip')
        print('Descargamos la imagen en un zip', output_path)

        download_url = f'https://download.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value'

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(download_url, headers=headers, stream=True)

        if response.status_code == 200:
            with open(output_path, 'wb') as writer:
                for chunk in response.iter_content(chunk_size=8192):
                    writer.write(chunk)
            print('Descarga del zip en ----->', output_path)
        else:
            print('Error al descargar el producto: Código de estado', response.status_code)
            raise Exception(f'Error al descargar el producto: Código de estado {response.status_code}')

    except Exception as error:
        print('Error al descargar el producto:', str(error))
        raise

import os
import shutil
import zipfile

import os
import zipfile
import shutil
import os
import zipfile
import shutil


def descomprimir_zips():
    # Directorio actual donde se encuentra la carpeta "imagenes"
    current_dir = os.getcwd()
    imagenes_dir = os.path.join(current_dir, 'imagenes')
    error_dir = os.path.join(current_dir, 'error')

    # Asegurarnos de que las carpetas 'imagenes' y 'error' existan
    os.makedirs(imagenes_dir, exist_ok=True)
    os.makedirs(error_dir, exist_ok=True)

    # Recorrer las informaciones y descomprimir los archivos ZIP
    for info in informaciones:
        product_name = info[1]  # El nombre del archivo descargado (sin la extensión .zip)
        print(product_name)
        zip_file_path = current_dir + f"/{product_name}.zip"  # Ruta del archivo .zip
        print(zip_file_path)



        try:
            # Intentar descomprimir el archivo .zip
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Crear una carpeta con el nombre del archivo (sin extensión) para descomprimir
                extract_dir = os.path.join(imagenes_dir, product_name)
                os.makedirs(extract_dir, exist_ok=True)
                zip_ref.extractall(extract_dir)
            print(f"Archivo {product_name}.zip descomprimido en {extract_dir}")
        
        except :
            # Si no es un archivo zip válido, moverlo a la carpeta "error"
            print(f"Error: {product_name}.zip no es un archivo válido. Moviéndolo a la carpeta 'error'.")

def get_satelite_polygon_coordinates(muestra):
    return {
        'nw': to_lat_lon(muestra.utmX - distance, muestra.utmY - distance, muestra.timeZone),
        'ne': to_lat_lon(muestra.utmX + distance, muestra.utmY - distance, muestra.timeZone),
        'se': to_lat_lon(muestra.utmX + distance, muestra.utmY + distance, muestra.timeZone),
        'sw': to_lat_lon(muestra.utmX - distance, muestra.utmY + distance, muestra.timeZone),
    }
def satelite_polygon_coordinates_to_acolite_limit(muestra):
    """
    Esta función toma las coordenadas de un polígono satelital y las convierte
    en el formato esperado para Acolite, similar a la función TypeScript original.
    """
    square_coordinates=get_satelite_polygon_coordinates(madrid_muestra)
    nw = square_coordinates['nw']
    se = square_coordinates['se']
    
    return f"{nw['latitude']},{nw['longitude']},{se['latitude']},{se['longitude']}"


def to_lat_lon(utmX, utmY, timeZone):
    lon, lat = transformer.transform(utmX, utmY)
    print('****************',lon,lat)
    return {'latitude': lat, 'longitude': lon}

def satelite_polygon_coordinates_to_query(square_coordinates):
    return (
        'POLYGON((' +
        f"{square_coordinates['nw']['longitude']} {square_coordinates['nw']['latitude']}, " +
        f"{square_coordinates['ne']['longitude']} {square_coordinates['ne']['latitude']}, " +
        f"{square_coordinates['se']['longitude']} {square_coordinates['se']['latitude']}, " +
        f"{square_coordinates['sw']['longitude']} {square_coordinates['sw']['latitude']}, " +
        f"{square_coordinates['nw']['longitude']} {square_coordinates['nw']['latitude']}))"
    )

def coger(response_json):
    entries = response_json.get('value', [])
    if not entries:
        print("No se encontraron entradas en la respuesta.")
        return []

    for i in range(len(entries)):
        fileName = entries[i]['Name']
        downloadUrl = COPERNICUS_OPEN_SEARCH_URL + '/' + entries[i]['Id']
        endPosition = entries[i]['ContentDate']['End']

        informaciones.append((downloadUrl, fileName, endPosition))
    return informaciones

def get_satelite_muestras(muestras):
    modo = [' gt ', ' asc', 'SENTINEL-2', 'MSIL1C']

    for muestra in muestras:
        begin_date = datetime.datetime.utcnow()
        if muestra.firstImage:
            begin_date = muestra.firstImage
        else:
            raise ValueError('No se encontró una fecha válida para las imágenes satelitales.')

        begin_date = begin_date.replace(hour=23, minute=59, second=59)
        to_date = begin_date

        satelite_polygon_coordinates = get_satelite_polygon_coordinates(muestra)
        completion_date = to_date.isoformat()
        coordenadas = satelite_polygon_coordinates_to_query(satelite_polygon_coordinates)
        print(coordenadas)

        filter_query = (f"$filter=Collection/Name eq '{modo[2]}' and "
                        f"contains(Name,'{modo[3]}') and "
                        f"ContentDate/Start {modo[0]} {completion_date}")
        query = (f"{COPERNICUS_OPEN_SEARCH_URL}?{filter_query} and "
                 f"OData.CSC.Intersects(Footprint,geography'SRID=4326;{coordenadas}')&"
                 f"$orderby=ContentDate/Start {modo[1]}")

        response = requests.get(query)
        if response.status_code == 200:
            response_json = response.json()
            informaciones = coger(response_json)
            print("Informaciones obtenidas:", informaciones)
        else:
            print(f"Error en la solicitud: {response.status_code}")
    return informaciones

def crear_carpetas_y_archivos():
    # Ruta actual
    current_dir = os.getcwd()

    # 1º Crear una carpeta llamada 'plantillas'
    plantillas_dir = os.path.join(current_dir, 'plantillas')
    os.makedirs(plantillas_dir, exist_ok=True)

    # 2º Crear los archivos de texto dentro de la carpeta 'plantillas'
    archivos_contenido = {
        'settings.txt.tpl': """inputfile=${INPUT-FILE}
output=/output
limit=40.43918148084956,-4.258400981846755,40.539181481065874,-4.058400958233731
EARTHDATA_u=${EARTHDATA-USER}
EARTHDATA_p=${EARTHDATA-PASSWORD} 
elevation=${ELEVATION}
map_title=False
lut_pressure=True
dem_pressure=False
dem_pressure_percentile=25
cams_grib_ancillary=None
sky_correction=True
sky_correction_option=rsky_new
glint_correction=True
glint_force_band=None
glint_mask_rhos_band=1600
glint_mask_rhos_threshold=0.05
glint_write_rhog_ref=False
glint_write_rhog_all=False
dsf_path_reflectance=tiled
dsf_spectrum_option=dark_list
dsf_full_scene=False
dsf_model_selection=min_drmsd
dsf_list_selection=intercept
dsf_tile_dims=None
dsf_min_tile_cover=0.10
dsf_min_tile_aot=0.01
dsf_plot_retrieved_tiles=True
dsf_plot_dark_spectrum=True
dsf_write_tiled_parameters=False
dsf_wave_range=400,900
dsf_exclude_bands=,
extra_ac_parameters=False
dsf_fixed_aot=None
dsf_fixed_lut=PONDER-LUT-201704-MOD2
exp_swir_threshold=0.0215
exp_fixed_epsilon=True
exp_fixed_epsilon_percentile=50
exp_fixed_aerosol_reflectance=True
exp_fixed_aerosol_reflectance_percentile=5
exp_wave1=1600
exp_wave2=2200
exp_alpha=None
exp_alpha_weighted=True
exp_epsilon=None
exp_gamma=None
s2_target_res=10
l8_output_bt=False
l8_output_lt_tirs=False
resolved_angles=False
resolved_angles_write=False
xy_output=False
gains=False
gains_l5_tm=1,1,1,1,1,1
gains_l7_etm=1,1,1,1,1,1
gains_l8_oli=1,1,1,1,1,1,1
gains_s2a_msi=1,1,1,1,1,1,1,1,1,1,1,1,1
gains_s2b_msi=1,1,1,1,1,1,1,1,1,1,1,1,1
merge_tiles=False
rgb_rhot=True
rgb_rhos=True
map_l2w=False
map_title=False
map_colorbar=False
map_colorbar_orientation=vertical
map_auto_range=True
map_fillcolor=LightGrey
rgb_red_wl=660
rgb_green_wl=560
rgb_blue_wl=480
rgb_min=0.0,0.0,0.0
rgb_max=0.15,0.15,0.15
rgb_pan_sharpen=False
map_projected=True
map_raster=True
map_scalebar=True
map_scalepos=UL
map_scalecolor=White
map_scalecolor_rgb=White
map_scalelen=None
map_colorbar_edge=True
map_max_dim=1000
map_points=None
l1r_nc_compression=True
l2r_nc_compression=True
l2w_nc_compression=True
l1r_nc_delete=True
l2r_nc_delete=True
l2w_nc_delete=True
l2w_nc_scaled=False
l2w_nc_scaled_offset=0.02
l2w_nc_scaled_factor=0.0001
l2r_export_geotiff=True
l2w_export_geotiff=True
export_geotiff_coordinates=False
#luts=PONDER-LUT-201704-MOD1,PONDER-LUT-201704-MOD2
slicing=False"""
    }

    for filename, content in archivos_contenido.items():
        file_path = os.path.join(plantillas_dir, filename)
        with open(file_path, 'w') as file:
            file.write(content.strip())

    # 3º Crear la carpeta 'imagenes'
    imagenes_dir = os.path.join(current_dir, 'imagenes')
    os.makedirs(imagenes_dir, exist_ok=True)

    print(f"Carpetas y archivos creados en: {current_dir}")

# Ejecutar la función 
import os
import subprocess

def modificar_settings_y_ejecutar_acolite(madrid_muestra:Muestras,elevation:int):
    # Directorio actual
    current_dir = os.getcwd()
   
    # Directorio de plantillas
    plantillas_dir = os.path.join(current_dir, 'plantillas')
    settings_tpl_path = os.path.join(plantillas_dir, 'settings.txt.tpl')
   
    # Verificar si el archivo tpl existe
    if not os.path.exists(settings_tpl_path):
        print(f"Error: El archivo {settings_tpl_path} no existe.")
         
   
    # Crear una copia del archivo settings.txt.tpl con las modificaciones
    with open(settings_tpl_path, 'r') as template_file:
        settings_content = template_file.read()
   
    # Definir el nombre del archivo y la carpeta de entrada
    input_filename = 'S2B_MSIL1C_20220131T111209_N0400_R137_T30TVK_20220131T115433.SAFE'  # Nombre de archivo y carpeta
    input_filepath = os.path.join(current_dir, 'imagenes', input_filename, input_filename)  # Ruta completa a la carpeta .SAFE
   
    # Verificar si la carpeta de entrada existe
    if not os.path.exists(input_filepath):
        print(f"Error: La carpeta de entrada {input_filepath} no existe.")
        return
     
    # Obtener las coordenadas del polígono (esto es un ejemplo, ajusta según tu lógica)
 
    polygon_coordinates = get_satelite_polygon_coordinates(madrid_muestra)
    limit_str = satelite_polygon_coordinates_to_query(polygon_coordinates)  # Convertir a cadena de texto
   
    # Modificar el contenido para reemplazar los parámetros
    settings_content = settings_content.replace('${EARTHDATA-USER}', 'bravo1996')
    settings_content = settings_content.replace('${EARTHDATA-PASSWORD}', 'scottex88S')
    settings_content = settings_content.replace('${limit}',satelite_polygon_coordinates_to_acolite_limit(madrid_muestra))
    settings_content = settings_content.replace('${INPUT-FILE}', '\\'+input_filename)  # Ruta completa a la carpeta .SAFE
    settings_content = settings_content.replace('${ELEVATION}', elevation)  # Establecer la altura a 600
       
    # Definir el path y el contenido del archivo settings.txt
    final_settings_path = os.path.join(os.path.join(current_dir, 'imagenes', input_filename), 'settings.txt')
    
    # Escribir el contenido de settings.txt
    with open(final_settings_path, 'w', encoding='utf-8') as settings_file:
        settings_file.write(settings_content)
    print(f"Archivo settings.txt escrito en {os.path.join(current_dir, 'imagenes', input_filename)}")
    
    # Definir el path donde se creará el archivo 'docker-compose.yml'
    a = os.path.join(current_dir, 'imagenes', input_filename)
    
    # Crear el contenido de 'acolite-docker-compose.yml'
    docker_compose_content = f"""
    services:
      acolite:
        image: acolite/acolite:tact_20231017
        volumes:
          - '{a}:/input'  # Montar la carpeta SAFE como /input en el contenedor
          - '{a}/output:/output'  # La salida será escrita en la carpeta actual
        command: ["acolite", "run", "--settings", "/input/settings.txt"]
    """
    
    # Escribir el contenido del archivo YAML con codificación UTF-8
    docker_compose_path = os.path.join(current_dir, 'imagenes', input_filename, 'docker-compose.yml')
    with open(docker_compose_path, 'w', encoding='utf-8') as docker_compose_file:
        docker_compose_file.write(docker_compose_content)
    
    print(f"Archivo docker-compose.yml escrito en {docker_compose_path}")
        # Comando Docker para ejecutar Acolite usando docker-compose
    docker_command = [
            'docker-compose', '-f', docker_compose_path,
            'up', '--remove-orphans'
        ]
       
        # Ejecutar Acolite con docker-compose
    try:
            result = subprocess.run(docker_command, cwd=current_dir, capture_output=True, text=True)
            print("Salida estándar:", result.stdout)
            print("Salida de error:", result.stderr)
            print(f"Ejecución de Acolite completada.")
    except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar Acolite: {e}")

# Ejecutar la función

get_satelite_muestras([madrid_muestra])
modificar_settings_y_ejecutar_acolite()

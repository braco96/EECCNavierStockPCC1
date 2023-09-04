# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 14:11:19 2024

@author: Luisbra
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 14:25:04 2024

@author: Luisbra
""" 
# Objeto con coordenadas de Madrid (aproximadamente)
import datetime
import os
import zipfile
import shutil
import requests
from pyproj import Proj, Transformer

class Muestras:
    def __init__(self, utmX, utmY, timeZone, firstImage, lastImage=None):
        self.utmX = utmX
        self.utmY = utmY
        self.timeZone = timeZone
        self.firstImage = firstImage


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
        'settings.txt.tpl': """## ACOLITE settings
## Written at 2024-11-06 14:27:25

copy_datasets=lon,lat,sza,vza,raa,rhot_*
s2_write_vaa=False
s2_write_saa=False
dsf_aot_estimate=tiled
dsf_spectrum_option=intercept
dsf_wave_range=400,900
s2_target_res=10
resolved_geometry=True
gains_toa=1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0
offsets_toa=0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
dsf_intercept_pixels=200
dsf_tile_dimensions=600,600
geometry_per_band=False
geometry_fixed_footprint=False
luts_reduce_dimensions=True
rgb_rhos=True
region_name=
limit_buffer=None
sub=None
polygon_limit=True
polygon="str(POLYGON((-3.9292 40.5913, -3.9292 40.5917, -3.9290 40.5917, -3.9290 40.5913, -3.9292 40.5913)))"
polylakes=False
polylakes_database=worldlakes
merge_tiles=False
merge_zones=True
extend_region=False
l1r_crop=False
add_band_name=False
compute_contrabands=False
netcdf_projection=True
netcdf_compression=False
netcdf_compression_level=4
netcdf_compression_least_significant_digit=None
netcdf_discretisation=False
landsat_qa_bands=PIXEL,RADSAT,SATURATION
landsat_qa_output=False
s2_include_auxillary=False
s2_project_auxillary=True
s2_write_dfoo=False
s2_dilate_blackfill=False
s2_dilate_blackfill_iterations=2
geometry_type=grids_footprint
geometry_res=60
geometry_override=False
smile_correction=True
smile_correction_tgas=True
use_tpg=True
use_supplied_ancillary=True
inputfile_swir=None
worldview_reproject=False
worldview_reproject_resolution=2.0
worldview_reproject_method=nearest
planet_store_sr=False
pleiades_skip_pan=False
prisma_rhot_per_pixel_sza=True
prisma_store_l2c=False
prisma_store_l2c_separate_file=True
prisma_output_pan=False
chris_interband_calibration=False
chris_noise_reduction=True
desis_mask_ql=True
clear_scratch=True
gf_reproject_to_utm=False
viirs_option=img+mod
viirs_scanline_projection=True
viirs_scanline_width=32
viirs_quality_flags=4,8,512,1024,2048,4096
viirs_output_tir=True
viirs_output_tir_lt=False
viirs_mask_mband=True
viirs_mask_immixed=True
viirs_mask_immixed_rat=False
viirs_mask_immixed_dif=True
viirs_mask_immixed_bands=I03/M10
viirs_mask_immixed_maxrat=0.2
viirs_mask_immixed_maxdif=0.002
tact_run=False
tact_profile_source=era5
tact_reptran=medium
tact_emissivity=water
tact_emissivity_file=None
tact_output_atmosphere=False
tact_output_intermediate=False
tact_map=True
ged_fill=True
tact_range=3.5,14.0
eminet_water_fill=True
eminet_water_threshold=0.0215
eminet_model_version=20220809
eminet_netname=Net2
eminet_fill=True
eminet_fill_dilate=False
verbosity=5
output_lt=False
solar_irradiance_reference=Coddington2021_1_0nm
blackfill_skip=True
blackfill_max=1.0
blackfill_wave=1600
output_bt=False
l2w_parameters=reproject_projection_resampling_method=bilinear,elevation=1000,map_dpi=90000,rhos_*,rhow_*,Rrs_*,tur_nechad2009ave,spm_nechad2010,spm_nechad2010ave,tur_nechad2009,tur_nechad2016,tur_dogliotti2015,tur_novoa2017,spm_novoa2017,chl_oc2,chl_oc3,chl_re_gons,chl_re_gons740,chl_re_moses3b,chl_re_moses3b740,chl_re_mishra,ndci,chl_re_bramich,ndvi,ndvi_rhot,CDOM_SAICA_mean,CDOM_DG_SAICA_mean,l2w_mask_water_parameters=True,l2r_export_geotiff=True,l2w_export_geotiff=True,export_cloud_optimized_geotiff=True,l2r_export_geotiff_rgb=True,l1r_delete_netcdf=True,l2r_delete_netcdf=True,l2w_delete_netcdf=True,rgb_rhow=True,merge_tiles=True,map_l2w=True,s2_target_res=10
l2w_mask=True
l2w_mask_wave=1600
l2w_mask_threshold=0.0215
l2w_mask_water_parameters=True
l2w_mask_negative_rhow=True
l2w_mask_negative_wave_range=400,900
l2w_mask_cirrus=True
l2w_mask_cirrus_threshold=0.005
l2w_mask_cirrus_wave=1373
l2w_mask_high_toa=True
l2w_mask_high_toa_threshold=0.3
l2w_mask_high_toa_wave_range=400,2500
l2w_mask_mixed=True
l2w_data_in_memory=False
nechad_range=600,900
nechad_max_rhow_C_factor=0.5
l2w_mask_smooth=True
l2w_mask_smooth_sigma=3
flag_exponent_swir=0
flag_exponent_cirrus=1
flag_exponent_toa=2
flag_exponent_negative=3
flag_exponent_outofscene=4
flag_exponent_mixed=5
atmospheric_correction=True
aerosol_correction=dark_spectrum
min_tgas_aot=0.85
min_tgas_rho=0.7
sza_limit_replace=False
sza_limit=79.999
vza_limit_replace=False
vza_limit=71.999
cirrus_correction=False
cirrus_range=1350.0,1390.0
cirrus_g_vnir=1.0
cirrus_g_swir=0.5
ancillary_data=True
ancillary_type=GMAO_MERRA2_MET
uoz_default=0.3
uwv_default=1.5
pressure=1013.25
pressure_default=1013.25
elevation=None
dem_pressure=False
dem_pressure_resolved=True
dem_pressure_percentile=25.0
dem_pressure_write=False
dem_source=copernicus30
dsf_interface_reflectance=False
dsf_interface_option=default
dsf_interface_lut=ACOLITE-RSKY-202102-82W
wind=None
wind_default=2.0
dsf_residual_glint_correction=False
dsf_residual_glint_correction_method=default
dsf_residual_glint_wave_range=1500,2400
glint_force_band=None
glint_mask_rhos_wave=1600
glint_mask_rhos_threshold=0.05
glint_write_rhog_ref=False
glint_write_rhog_all=False
adjacency_correction=False
adjacency_method=acstar3
acstar3_method=iter
acstar3_psf_raster=False
acstar3_max_wavelength=720.0
acstar3_fit_all_bands=True
acstar3_write_rhosu=True
acstar3_write_rhoa=True
acstar3_write_rhoe=True
acstar3_ex=3
acstar3_mask_edges=True
radcor_initial_aot=0.3
radcor_psf_radius=3.5
radcor_psf_rescale=False
radcor_psf_complete_method=neighborhood
radcor_force_model=None
radcor_force_aot=None
radcor_force_tgas=False
radcor_force_glint=False
radcor_rho_calc=None
"""
    }

    for filename, content in archivos_contenido.items():
        file_path = os.path.join(plantillas_dir, filename)
        with open(file_path, 'w') as file:
            file.write(content.strip())

    # 3º Crear la carpeta 'imagenes'
    imagenes_dir = os.path.join(current_dir, 'imagenes')
    os.makedirs(imagenes_dir, exist_ok=True)

    print(f"Carpetas y archivos creados en: {current_dir}")
import os
import subprocess
import stat

def modificar_settings_y_ejecutar_acolite(madrid_muestra, elevation):
    # Directorio actual
    current_dir = os.getcwd()
   
    # Directorio de plantillas
    plantillas_dir = os.path.join(current_dir, 'plantillas')
    settings_tpl_path = os.path.join(plantillas_dir, 'settings.txt.tpl')
   
    # Verificar si el archivo tpl existe
    if not os.path.exists(settings_tpl_path):
        print(f"Error: El archivo {settings_tpl_path} no existe.")
        return
   
    # Leer el contenido del archivo de plantilla settings.txt.tpl
    with open(settings_tpl_path, 'r') as template_file:
        settings_content = template_file.read()
   
    # Definir el nombre del archivo y la carpeta de entrada
    input_filename = 'S2B_MSIL1C_20220131T111209_N0400_R137_T30TVK_20220131T115433.SAFE'
    input_folder_path = os.path.join(current_dir, 'imagenes', input_filename)
    input_filepath = os.path.join(current_dir, 'imagenes', input_filename,input_filename)

    # Verificar si la carpeta de entrada existe
    if not os.path.exists(input_folder_path):
        print(f"Error: La carpeta de entrada {input_folder_path} no existe.")
        return
    
    # Modificar el contenido de settings.txt para incluir comillas alrededor del input 
    settings_content = settings_content.replace('${INPUT-FILE}', f'"{input_filepath.replace("\\", "/")}"')  # Agregar comillas
 
       
    # Escribir el archivo settings.txt
    final_settings_path = os.path.join(input_folder_path, 'settings.txt')
    with open(final_settings_path, 'w', encoding='utf-8') as settings_file:
        settings_file.write(settings_content)
    print(f"Archivo settings.txt escrito en {final_settings_path}")
    
    # Crear el archivo docker-compose.yml
    docker_compose_content = f"""
    version: '3.8'
    services:
        satelitalmlacolite:
            image: 'acolite/acolite:tact_latest'
            volumes:
                - '{input_filepath.replace("\\", "/")}:/input'
                - './output:/output'
                - './settings.txt:/settings'
            command: 'python acolite_run.py /settings.txt'
    """
    
    # Escribir el archivo YAML
    docker_compose_path = os.path.join(input_folder_path, 'docker-compose.yml')
    with open(docker_compose_path, 'w', encoding='utf-8') as docker_compose_file:
        docker_compose_file.write(docker_compose_content)
    
    # Cambiar permisos del archivo docker-compose.yml
    os.chmod(docker_compose_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    
    print(f"Archivo docker-compose.yml escrito en {docker_compose_path}")
    
    # Ejecutar Acolite con docker-compose
    docker_command = [
        'docker-compose', '-f', docker_compose_path,
        'up', '--remove-orphans'
    ]
    try:
        result = subprocess.run(docker_command, cwd=current_dir, capture_output=True, text=True)
        print("Salida estándar:", result.stdout)
        print("Salida de error:", result.stderr)
        print("Ejecución de Acolite completada.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar Acolite: {e}")

# Ejecutar la función
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

fecha_actual = datetime.datetime.now()
fecha_hace_14_dias = fecha_actual - datetime.timedelta(days=994)
madrid_muestra = Muestras(utmX=410369, utmY=4488142, timeZone=30, firstImage=fecha_hace_14_dias)
muestra = [madrid_muestra]

utm_proj = Proj(proj="utm", zone=30, ellps="WGS84")
transformer = Transformer.from_proj(utm_proj, wgs84_proj)
COPERNICUS_OPEN_SEARCH_URL = 'https://catalogue.dataspace.copernicus.eu/odata/v1/Products'
crear_carpetas_y_archivos()
modificar_settings_y_ejecutar_acolite(madrid_muestra,"300")
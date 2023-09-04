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

import os
import shutil
import zipfile

import os
import zipfile
import shutil
import os
import zipfile
import shutil

import json
    

from pyproj import Proj, Transformer 
wgs84_proj = Proj(proj="latlong", datum="WGS84") 
client_id = 'cdse-public'
username = 'bravocolladoluis@gmail.com'
password = '9YK6XF?@$jbMz_T'
grant_type = 'password'
token_url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'


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
    def __init__(self, utmX:None, utmY:None,polygono:None ,timeZone:None, firstImage):
        self.firstImage = firstImage
        self.cantidad = 5
        self.distance = 5000
        self.elevation=1000
        self.descargados = []
        self.coordenadas = ''
        self.informaciones = []
        if (utmX and utmY and timeZone) is not None:
                
                self.utmX = utmX
                self.utmY = utmY
                self.timeZone = timeZone
              
        
                # Inicialización de atributos
                self.polygondic = self.get_satelite_polygon_coordinates(None)
                self.limite = self.transformar_poligono_a_limites()
                self.polygonquery = self.satelite_polygon_coordinates_to_query()
        elif(polygono is not None):
                self.polygondic = self.get_satelite_polygon_coordinates(polygono)
                self.limite = self.transformar_poligono_a_limites()
                self.polygonquery = self.satelite_polygon_coordinates_to_query()
                

    def get_satelite_polygon_coordinates(self, polygono=None):
        try:
            return {
                'nw': self.to_lat_lon(self.utmX - self.distance, self.utmY - self.distance, self.timeZone),
                'ne': self.to_lat_lon(self.utmX + self.distance, self.utmY - self.distance, self.timeZone),
                'se': self.to_lat_lon(self.utmX + self.distance, self.utmY + self.distance, self.timeZone),
                'sw': self.to_lat_lon(self.utmX - self.distance, self.utmY + self.distance, self.timeZone),
            }
        except:
            # Aseguramos que el polígono tiene el formato esperado
            try:
                return {
                    'nw': {'longitude': str(polygono[0][0][0]), 'latitude': str(polygono[0][0][1])},
                    'sw': {'longitude': str(polygono[0][1][0]), 'latitude': str(polygono[0][1][1])},
                    'se': {'longitude': str(polygono[0][2][0]), 'latitude': str(polygono[0][2][1])},
                    'ne': {'longitude': str(polygono[0][3][0]), 'latitude': str(polygono[0][3][1])},
                }
            except (IndexError, TypeError) as e:
                print(f"Error al acceder al polígono: {e}")
                return None

    def to_lat_lon(self, utmX, utmY, timeZone):
        utm_proj = Proj(proj="utm", zone=timeZone, ellps="WGS84")
        wgs84_proj = Proj(proj="latlong", datum="WGS84")
        transformer = Transformer.from_proj(utm_proj, wgs84_proj)
        lon, lat = transformer.transform(utmX, utmY)
        return {'latitude': lat, 'longitude': lon}

    def transformar_poligono_a_limites(self): 
        longitude = [self.polygondic['nw']['longitude'], self.polygondic['ne']['longitude'], 
                     self.polygondic['se']['longitude'], self.polygondic['sw']['longitude']]
        latitude = [self.polygondic['nw']['latitude'], self.polygondic['ne']['latitude'], 
                    self.polygondic['se']['latitude'], self.polygondic['sw']['latitude']]

        # Calcular límites
        lat_sur = min(latitude)
        lat_norte = max(latitude)
        long_oeste = min(longitude)
        long_este = max(longitude)

        return f'{lat_sur}, {long_oeste}, {lat_norte}, {long_este}'

    def satelite_polygon_coordinates_to_query(self):
        ini='POLYGON(('
        fin='))'
        return (ini
                 +
                f"{self.polygondic['nw']['longitude']} {self.polygondic['nw']['latitude']}, " +
                f"{self.polygondic['ne']['longitude']} {self.polygondic['ne']['latitude']}, " +
                f"{self.polygondic['se']['longitude']} {self.polygondic['se']['latitude']}, " +
                f"{self.polygondic['sw']['longitude']} {self.polygondic['sw']['latitude']}, " +
                f"{self.polygondic['nw']['longitude']} {self.polygondic['nw']['latitude']}))"
            )
       
            
            

    def satelite_polygon_acolite(self, ruta):
        # Crear el diccionario del polígono
       try:
            polygon_data = {
                "type": "Polygon",
                "coordinates": [[
                    [self.polygondic['nw']['longitude'], self.polygondic['nw']['latitude']],
                    [self.polygondic['ne']['longitude'], self.polygondic['ne']['latitude']],
                    [self.polygondic['se']['longitude'], self.polygondic['se']['latitude']],
                    [self.polygondic['sw']['longitude'], self.polygondic['sw']['latitude']],
                    [self.polygondic['nw']['longitude'], self.polygondic['nw']['latitude']]
                ]]
            }
       except :
                polygon_data = {
                    "type": "Polygon",
                    "coordinates": self.polygondic
                }

        # Escribir el JSON a un archivo en la ruta dada
       with open(f"{ruta}/polygon.json", "w") as file:
            json.dump(polygon_data, file, indent=4)
    
       print(f"El archivo polygon.json se ha guardado en la ruta: {ruta}")




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

def descargar(muestras):
   
    for info in muestras.informaciones[:muestras.cantidad]:
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


def descomprimir_zips(muestra):
    # Directorio actual donde se encuentra la carpeta "imagenes"
    current_dir = os.getcwd()
    imagenes_dir = os.path.join(current_dir, 'imagenes')
    error_dir = os.path.join(current_dir, 'error')

    # Asegurarnos de que las carpetas 'imagenes' y 'error' existan
    os.makedirs(imagenes_dir, exist_ok=True)
    os.makedirs(error_dir, exist_ok=True)

    # Recorrer las informaciones y descomprimir los archivos ZIP
    for info in muestra.informaciones:
        product_name = info[1]  # El nombre del archivo descargado (sin la extensión .zip)
        print(product_name)
        zip_file_path = current_dir + f"/{product_name}.zip"  # Ruta del archivo .zip
        print(zip_file_path)

        # Crear una carpeta con el nombre del archivo (sin extensión) para descomprimir
        extract_dir = os.path.join(imagenes_dir, product_name)
        polygon = os.path.join(imagenes_dir, product_name)
        

        try:
            # Intentar descomprimir el archivo .zip
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                os.makedirs(extract_dir, exist_ok=True)
                zip_ref.extractall(extract_dir)
            print(f"Archivo {product_name}.zip descomprimido en {extract_dir}")
        
        except :
            # Si no es un archivo zip válido, moverlo a la carpeta "error"
            print(f"Error: {product_name}.zip no es un archivo válido. Moviéndolo a la carpeta 'error'.")


def coger(response_json,muestra):
    entries = response_json.get('value', [])
    if not entries:
        print("No se encontraron entradas en la respuesta.") 
        return []
  
    fileName = entries[0]['Name']
    downloadUrl = COPERNICUS_OPEN_SEARCH_URL + '/' + entries[0]['Id']
    endPosition = entries[0]['ContentDate']['Start']
    muestra.firstImage=datetime.datetime.strptime(endPosition , '%Y-%m-%dT%H:%M:%S.%fZ')
    
    muestra.informaciones.append([downloadUrl, fileName, endPosition])
    return muestra.informaciones

def get_satelite_muestras(muestra):
        modo = [' gt ', ' asc', 'SENTINEL-2', 'MSIL1C'] 
        begin_date = datetime.datetime.utcnow()
        if muestra.firstImage:
            begin_date = muestra.firstImage
        else:
            raise ValueError('No se encontró una fecha válida para las imágenes satelitales.')

        begin_date = begin_date.replace(hour=23, minute=59, second=59)
        to_date = begin_date
 
        completion_date = to_date.isoformat()
        coordenadas = muestra.polygonquery
        muestra.polygon=coordenadas
        print(coordenadas)

        filter_query = (f"$filter=Collection/Name eq '{modo[2]}' and "
                        f"contains(Name,'{modo[3]}') and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le 20.00) and "
                        f"ContentDate/Start {modo[0]} {completion_date}")
        query = (f"{COPERNICUS_OPEN_SEARCH_URL}?{filter_query} and "
                 f"OData.CSC.Intersects(Footprint,geography'SRID=4326;{coordenadas}')&"
                 f"$orderby=ContentDate/Start {modo[1]}")

        response = requests.get(query)
        print('---------------->')
        if response.status_code == 200:
            response_json = response.json()
            muestra.informaciones = coger(response_json,muestra)
            print("Informaciones obtenidas:", muestra.informaciones)
        else:
            print(f"Error en la solicitud: {response.status_code}")
        return muestra.informaciones

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
    limit=${LIMIT}
    map_title=False 
    blackfill_skip=True
    blackfill_max=1.0
    blackfill_wave=1600 
    l2w_parameters=reproject_projection_resampling_method=bilinear,elevation=1000,map_dpi=90000,rhos_*,rhow_*,Rrs_*,tur_nechad2009ave,spm_nechad2010,spm_nechad2010ave,tur_nechad2009,tur_nechad2016,tur_dogliotti2015,tur_novoa2017,spm_novoa2017,chl_oc2,chl_oc3,chl_re_gons,chl_re_gons740,chl_re_moses3b,chl_re_moses3b740,chl_re_mishra,ndci,chl_re_bramich,ndvi,ndvi_rhot,CDOM_SAICA_mean,CDOM_DG_SAICA_mean,l2w_mask_water_parameters=True,l2r_export_geotiff=True,l2w_export_geotiff=True,export_cloud_optimized_geotiff=True,l2r_export_geotiff_rgb=True,l1r_delete_netcdf=True,l2r_delete_netcdf=True,l2w_delete_netcdf=True,rgb_rhow=True,merge_tiles=True,map_l2w=True,s2_target_res=10
    l2w_mask=True
    l2w_mask_wave=1600
    l2w_mask_threshold=0.0215
    l2w_mask_water_parameters=True
    l2w_mask_negative_rhow=True
    l2w_mask_cirrus=True
    l2w_mask_cirrus_threshold=0.005
    aerosol_correction=dark_spectrum
    ancillary_data=True
    gas_transmittance=True
    uoz_default=0.3
    uwv_default=1.5
    pressure=1000 
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
    slicing=False

    """
    }
    archivos_contenido1 = {
        'settings.txt.tpl': """## ACOLITE settings
## Written at 2024-11-06 17:27:02
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
limit_buffer=None
sub=None
polygon_limit=True
polylakes=False
polylakes_database=worldlakes
merge_tiles=False
merge_zones=True
extend_region=False
l1r_crop=False
output_geolocation=True
output_xy=False
output_geometry=True
output_rhorc=False
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
radcor_expand_edge=True
radcor_expand_method=mirror
radcor_mask_edges=True
radcor_fft_stack=False
radcor_write_rhot=True
radcor_write_rhoe=True
radcor_bratio_option=percentile
radcor_bratio_percentile=1.0
dsf_nbands=2
dsf_nbands_fit=2
dsf_aot_compute=min
dsf_percentile=1.0
dsf_minimum_segment_size=1
dsf_allow_lut_boundaries=False
dsf_filter_rhot=False
dsf_filter_percentile=50.0
dsf_filter_box=10,10
dsf_filter_aot=False
dsf_smooth_aot=False
dsf_smooth_box=10,10
dsf_aot_fillnan=True
dsf_aot_most_common_model=True
dsf_model_selection=min_drmsd
dsf_min_tile_cover=0.1
dsf_min_tile_aot=0.01
dsf_max_tile_aot=1.2
dsf_write_tiled_parameters=False
dsf_exclude_bands=None
dsf_write_aot_550=False
dsf_fixed_aot=None
dsf_fixed_lut=ACOLITE-LUT-202110-MOD2
dsf_tile_smoothing=True
dsf_tile_smoothing_kernel_size=3
dsf_tile_interp_method=linear
exp_swir_threshold=0.0215
exp_fixed_epsilon=True
exp_fixed_epsilon_percentile=50.0
exp_fixed_aerosol_reflectance=True
exp_fixed_aerosol_reflectance_percentile=5.0
exp_wave1=1600
exp_wave2=2200
exp_alpha=None
exp_alpha_weighted=True
exp_epsilon=None
exp_gamma=None
exp_output_intermediate=False
gains=False
gains_parameter=radiance
offsets=False
rgb_rhot=True
rgb_rhorc=False
rgb_rhow=False
map_l2w=True
map_title=True
map_fontname=sans-serif
map_fontsize=12
map_usetex=False
map_dpi=300
map_ext=png
map_limit=None
map_scalebar=False
map_scalebar_position=UL
map_scalebar_color=Black
map_scalebar_length=None
map_scalebar_max_fraction=0.33
map_points=None
map_colorbar=True
map_colorbar_orientation=vertical
map_auto_range=False
map_auto_range_percentiles=1.0,99.0
map_fill_outrange=False
map_fill_color=LightGrey
map_default_colormap=viridis
rgb_red_wl=650
rgb_green_wl=560
rgb_blue_wl=480
rgb_min=0.0,0.0,0.0
rgb_max=0.15,0.15,0.15
rgb_gamma=1.0,1.0,1.0
rgb_autoscale=False
rgb_autoscale_percentiles=5.0,95.0
rgb_stretch=linear
pans=False
pans_method=panr
pans_output=rgb
pans_bgr=480,560,655
pans_rgb_rhot=True
pans_rgb_rhos=True
pans_export_geotiff_rgb=False
pans_sensors=L7_ETM,L8_OLI,L9_OLI
map_projected=False
map_raster=False
map_pcolormesh=False
map_cartopy=False
map_mask=True
map_xtick_rotation=0.0
map_ytick_rotation=0.0
map_gridline_color=white
l1r_export_geotiff=False
l2t_export_geotiff=False
l2r_export_geotiff=False
l2w_export_geotiff=False
export_geotiff_coordinates=False
export_geotiff_match_file=None
export_cloud_optimized_geotiff=False
l1r_export_geotiff_rgb=False
l2r_export_geotiff_rgb=False
use_gdal_merge_import=False
l1r_delete_netcdf=False
l2t_delete_netcdf=False
l2r_delete_netcdf=False
l2r_pans_delete_netcdf=False
l2w_delete_netcdf=False
delete_acolite_run_text_files=False
delete_acolite_output_directory=False
delete_extracted_input=False
reproject_outputs=L1R,L2R,L2W
reproject_before_ac=False
output_projection=False
output_projection_name=None
output_projection_epsg=None 
reproject_inputfile_force=False
reproject_inputfile_dem=False
luts=ACOLITE-LUT-202110-MOD1,ACOLITE-LUT-202110-MOD2
luts_pressures=500,750,1013,1100
slicing=False
scene_download=False
scene_download_directory=None
EARTHDATA_u=bravo1996
EARTHDATA_p=scottex88S
inputfile=${INPUT-FILE}
output=/output
limit=${LIMIT} 
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

# Ejecutar la función
crear_carpetas_y_archivos()
import os
import subprocess

def ejecutar_acolite(madrid_muestra:Muestras):
    for elem in madrid_muestra.informaciones:
        modificar_settings_y_ejecutar_acolite(madrid_muestra,elem[1])
    
def modificar_settings_y_ejecutar_acolite(madrid_muestra:Muestras,input_filename):
    # Directorio actual
    current_dir = os.getcwd()
   
    # Directorio de plantillas
    plantillas_dir = os.path.join(current_dir, 'plantillas')
    settings_tpl_path = os.path.join(plantillas_dir, 'settings.txt.tpl')
   
    # Verificar si el archivo tpl existe
    if not os.path.exists(settings_tpl_path):
        print(f"Error: El archivo {settings_tpl_path} no existe.")
        return
         
    # Crear una copia del archivo settings.txt.tpl con las modificaciones
    with open(settings_tpl_path, 'r') as template_file:
        settings_content = template_file.read()
   
    # Definir el nombre del archivo y la carpeta de entrada 
    input_filepath = os.path.join(current_dir, 'imagenes', input_filename, input_filename)  # Ruta completa a la carpeta .SAFE
    input_filepat = os.path.join(current_dir, 'imagenes', input_filename)
    # Verificar si la carpeta de entrada existe
    if not os.path.exists(input_filepath):
        print(f"Error: La carpeta de entrada {input_filepath} no existe.")
        return
     
    # Obtener las coordenadas del polígono (esto es un ejemplo, ajusta según tu lógica)
    # Ahora usando las coordenadas limit 
    os.makedirs(os.path.join(input_filepat,'output'), exist_ok=True)
    madrid_muestra.satelite_polygon_acolite(os.path.join(input_filepat,'output'))
    # Modificar el contenido para reemplazar los parámetros
    settings_content = settings_content.replace('${EARTHDATA-USER}', 'bravo1996')
    settings_content = settings_content.replace('${LIMIT}',madrid_muestra.limite)  # Reemplazar la clave limit con las coordenadas

    settings_content = settings_content.replace('${EARTHDATA-PASSWORD}', 'scottex88S') 
    settings_content = settings_content.replace('${INPUT-FILE}',  f'/input/{input_filename}' )  # Ruta completa a la carpeta .SAFE
    settings_content = settings_content.replace('${ELEVATION}', str(madrid_muestra.elevation))  # Establecer la altura a 600
    
    settings_content = settings_content.replace('${QUERY}',madrid_muestra.polygonquery)  # Reemplazar la clave limit con las coordenadas

    # Definir el path y el contenido del archivo settings.txt
    final_settings_path = os.path.join(os.path.join(current_dir, 'imagenes', input_filename), 'settings.txt')
    
    # Escribir el contenido de settings.txt
    with open(final_settings_path, 'w', encoding='utf-8') as settings_file:
        settings_file.write(settings_content)
    print(f"Archivo settings.txt escrito en {os.path.join(current_dir, 'imagenes', input_filename)}")
    
    # Definir el path donde se creará el archivo 'docker-compose.yml'
    
    # Crear el contenido de 'acolite-docker-compose.yml'
    docker_compose_content = f"""
    services:
        satelitalmlacolite:
            volumes:
                - '{input_filepat}:/input'
                - './output:/output'
                - './settings.txt:/settings'
            image: 'acolite/acolite:tact_latest'
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


 

fecha_actual = datetime.datetime.now()
fecha_hace_14_dias = fecha_actual - datetime.timedelta(days=994)
madrid_muestra3 = Muestras(utmX=410655, utmY=4488157,polygono=None, timeZone=30, firstImage=fecha_hace_14_dias)
madrid_muestra = Muestras(utmX=None, utmY=None,polygono= 
[
          
          [
            [
              -4.1251473934840135,
              40.60140928690248
            ],
            [
              -4.1251473934840135,
              40.50499208097915
            ],
            [
              -3.9946251084963933,
              40.50499208097915
            ],
            [
              -3.9946251084963933,
              40.60140928690248
            ],
            [
              -4.1251473934840135,
              40.60140928690248
            ]
          ]
        ], timeZone=30, firstImage=fecha_hace_14_dias) 

#COGEMOS 1  
get_satelite_muestras(madrid_muestra)    


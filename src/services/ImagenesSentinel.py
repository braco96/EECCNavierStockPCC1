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
from shapely.geometry import Polygon     
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


import os
import requests
import datetime
import zipfile
from shapely.geometry import Polygon

class ImagenesSentinel:
    def __init__(self, muestra):
        self.muestra = muestra

    def contiene(self, grande, peque):
        print('polygono grande ----------->', grande)
        print('polygono grande ----------->', peque)
        outer_gran = Polygon(grande[0])
        inner_peq = Polygon(peque[0])
        return outer_gran.contains(inner_peq)

    def get_access_token(self) -> str:
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

    def descargar(self):
        for info in self.muestra.informaciones[:self.muestra.cantidad]:
            product_url = info[0]
            product_name = info[1]
            self.download_product(self.get_access_token(), product_url, product_name)

    def download_product(self, access_token: str, product_url: str, name: str) -> None:
        try:
            product_id = product_url.split('/')[-1]
            print('Comenzamos una descarga')
            print('Nombre', name)
            print('Producto', product_id)

            download_path = self.muestra.ubicacion
            output_path = os.path.join(download_path, f'{name}.zip')
            print('Descargamos la imagen en un zip', output_path)

            download_url = f'https://download.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value'
            headers = {'Authorization': f'Bearer {access_token}'}
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
    import zipfile
    import shutil  # Para mover archivos
    
   
    def descomprimir_zips(self):
        current_dir = self.muestra.ubicacion
        
        imagenes_dir = os.path.join(current_dir, 'imagenes')
        error_dir = os.path.join(current_dir, 'error')

        os.makedirs(imagenes_dir, exist_ok=True)
        os.makedirs(error_dir, exist_ok=True)

        for info in self.muestra.informaciones:
            product_name = info[1]
            print(product_name)
            zip_file_path = current_dir + f"/{product_name}.zip"
            print(zip_file_path)

            extract_dir = os.path.join(imagenes_dir, product_name)

            try:
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    os.makedirs(extract_dir, exist_ok=True)
                    zip_ref.extractall(extract_dir)
                print(f"Archivo {product_name}.zip descomprimido en {extract_dir}")

            except:
                print(f"Error: {product_name}.zip no es un archivo válido. Moviéndolo a la carpeta 'error'.")
 
    def coger(self, response_json):
        entries = response_json.get('value', [])
        if not entries:
            print("No se encontraron entradas en la respuesta.")
            return []
        for i in entries:
            if self.muestra.cantidad > len(self.muestra.informaciones):
                fileName = i['Name']
                downloadUrl = COPERNICUS_OPEN_SEARCH_URL + '/' + i['Id']
                endPosition = i['ContentDate']['Start']
                fecha = datetime.datetime.strptime(endPosition, '%Y-%m-%dT%H:%M:%S.%fZ')
                if self.contiene(i['GeoFootprint']['coordinates'], self.muestra.polygono):
                    self.muestra.informaciones.append([downloadUrl, fileName, endPosition])
                else:
                    print('No se contienen')
        return self.muestra.informaciones

    def get_satelite_muestras(self):
        modo = [' gt ', ' asc', 'SENTINEL-2', 'MSIL1C']
        begin_date = datetime.datetime.utcnow()
        if self.muestra.firstImage:
            begin_date = self.muestra.firstImage
        else:
            raise ValueError('No se encontró una fecha válida para las imágenes satelitales.')

        begin_date = begin_date.replace(hour=23, minute=59, second=59)
        to_date = begin_date
        completion_date = to_date.isoformat()
        coordenadas = self.muestra.polygonquery
        self.muestra.polygon = coordenadas
        print(coordenadas)

        filter_query = (f"$filter=Collection/Name eq '{modo[2]}' and "
                        f"contains(Name,'{modo[3]}') and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le 20.00) and "
                        f"ContentDate/Start {modo[0]} {completion_date}")
        query = (f"{COPERNICUS_OPEN_SEARCH_URL}?{filter_query} and "
                 f"OData.CSC.Intersects(Footprint,geography'SRID=4326;{coordenadas}')&"
                 f"$orderby=ContentDate/Start {modo[1]} $top=100")

        response = requests.get(query)
        print('---------------->', query)
        if response.status_code == 200:
            response_json = response.json()
            self.muestra.informaciones = self.coger(response_json)
            print("Informaciones obtenidas:", self.muestra.informaciones)
        else:
            print(f"Error en la solicitud: {response.status_code}")
        return self.muestra.informaciones
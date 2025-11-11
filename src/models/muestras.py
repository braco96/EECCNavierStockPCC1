import os
import subprocess
import json
from pyproj import Proj, Transformer
import traceback  # Opcional para imprimir errores  
class Muestras:
    def __init__(self, utmX:None, utmY:None,polygono:None ,timeZone:None, firstImage):
        self.firstImage = firstImage
        self.cantidad = 1
        self.distance = 5000
        self.elevation=1000
        self.descargados = []
        self.coordenadas = ''
        self.informaciones = []
        self.ubicacion=(os.path.dirname(os.getcwd()))
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
                self.polygono=polygono
               

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
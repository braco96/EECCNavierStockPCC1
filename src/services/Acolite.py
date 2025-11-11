import os
import subprocess 
from models.muestras import Muestras
class Acolite :
    def __init__(self, muestra:Muestras):
            self.muestra=muestra
            self.ejecutar_acolite()
    def ejecutar_acolite(self):
        for elem in self.muestra.informaciones:
            self.modificar_settings_y_ejecutar_acolite(elem[1])
       
    def modificar_settings_y_ejecutar_acolite(self,input_filename):
        # Directorio actual
        current_dir = self.muestra.ubicacion
       
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
        self.muestra.satelite_polygon_acolite(os.path.join(input_filepat,'output'))
        # Modificar el contenido para reemplazar los parámetros
        settings_content = settings_content.replace('${EARTHDATA-USER}', 'bravo1996')
        settings_content = settings_content.replace('${LIMIT}',self.muestra.limite)  # Reemplazar la clave limit con las coordenadas
    
        settings_content = settings_content.replace('${EARTHDATA-PASSWORD}', 'scottex88S')
        settings_content = settings_content.replace('${INPUT-FILE}',  f'/input/{input_filename}' )  # Ruta completa a la carpeta .SAFE
        settings_content = settings_content.replace('${ELEVATION}', str(self.muestra.elevation))  # Establecer la altura a 600
       
        settings_content = settings_content.replace('${QUERY}',self.muestra.polygonquery)  # Reemplazar la clave limit con las coordenadas
    
        # Definir el path y el contenido del archivo settings.txt
        final_settings_path = os.path.join(os.path.join(current_dir, 'imagenes', input_filename), 'settings.txt')
       
        # Escribir el contenido de settings.txt
        with open(final_settings_path, 'w', encoding='utf-8') as settings_file:
            settings_file.write(settings_content)
        print(f"Archivo settings.txt escrito en {os.path.join(current_dir, 'imagenes', input_filename)}")
       
        # Definir el path donde se creará el archivo 'docker-compose.yml'
       
        # Crear el contenido de 'acolite-docker-compose.yml'
        docker_compose_content = f"""services:
            acolite:
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
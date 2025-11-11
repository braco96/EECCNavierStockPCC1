import os
import shutil

class Simulacion:
    def __init__(self, muestra, parametros_completos):
        self.muestra = muestra
        self.parametros = parametros_completos
        self.hijos = []
        self.parameters = []

    def ejecutar_simulacion(self):
        for a in self.muestra.informaciones:
            current_dir = self.muestra.ubicacion  
            output_dir = os.path.join(current_dir, 'imagenes', a[1], 'output')
            simulacion_dir = os.path.join(current_dir, 'simulacion')

            # Creamos el directorio de simulación si no existe
            os.makedirs(simulacion_dir, exist_ok=True)

            # Recorremos cada parámetro en 'parametros_completos'
            for parametro in self.parametros:
                # Creamos el nombre de la carpeta
                nombre_carpeta = f"{parametro['raiz']}{parametro['año']}{parametro['banda']}"
                ruta_destino = os.path.join(simulacion_dir, nombre_carpeta)
                os.makedirs(ruta_destino, exist_ok=True)

                # Verificamos los archivos dentro de la carpeta output
                if not os.path.exists(output_dir):
                    print(f"El directorio {output_dir} no existe.")
                    continue

                archivos = os.listdir(output_dir)
                archivos_movidos = []

                for archivo in archivos:
                    if (parametro['raiz'] in archivo and 
                        parametro['año'] in archivo and 
                        parametro['banda'] in archivo):
                        
                        archivo_origen = os.path.join(output_dir, archivo)
                        archivo_destino = os.path.join(ruta_destino, archivo)

                        if os.path.exists(archivo_origen):
                            shutil.move(archivo_origen, archivo_destino)
                            archivos_movidos.append(archivo)
                            print(f"Archivo {archivo} movido a: {archivo_destino}")

                        # Actualizamos la lista de 'informaciones' de la muestra con la nueva ruta
                        for info in self.muestra.informaciones:
                            if info[0] == archivo:
                                info[1] = archivo_destino

                # Actualizamos el parámetro con atributos adicionales
                cantidad = len(archivos_movidos)
                parametro['intervalo'] = f"[a,b]"
                parametro['ruta_carpeta'] = ruta_destino
                parametro['cantidad'] = cantidad
                parametro['ruta_hijos'] = [os.path.join(ruta_destino, f) for f in archivos_movidos]

                # Depuración
                print(f"Parámetro: {parametro['raiz']} {parametro['año']} {parametro['banda']}")
                print(f"Intervalo: {parametro['intervalo']}")
                print(f"Ruta carpeta: {parametro['ruta_carpeta']}")
                print(f"Cantidad: {parametro['cantidad']}")
                print(f"Ruta hijos: {parametro['ruta_hijos']}")

        print("Simulación completada.")

    def hijos(self): 
        simulacion_data = []
        ruta_simulacion = os.path.join(self.muestra.ubicacion, 'simulacion')
        self.hijos = []

        if not os.path.exists(ruta_simulacion):
            print(f"La ruta {ruta_simulacion} no existe.")
            return simulacion_data

        for parametro in self.parametros:
            nombre_carpeta = f"{parametro['raiz']}{parametro['año']}{parametro['banda']}"
            ruta_destino = os.path.join(ruta_simulacion, nombre_carpeta)

            if os.path.exists(ruta_destino):
                archivos = os.listdir(ruta_destino)

                parametro_info = {
                    'nombre': nombre_carpeta,
                    'intervalo': parametro.get('intervalo', 'N/A'),
                    'ruta_carpeta': ruta_destino,
                    'cantidad': len(archivos),
                    'ruta_hijos': [os.path.join(ruta_destino, a) for a in archivos],
                    'archivos': archivos
                }
                self.hijos.extend([os.path.join(nombre_carpeta, a) for a in archivos])
                simulacion_data.append(parametro_info)

        self.parameters = simulacion_data
        print(f"Información de simulación: {simulacion_data}")

from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
from models.muestras import Muestras
from models.simulacion import Simulacion
from services.ImagenesSentinel import ImagenesSentinel
from services.Acolite import Acolite
from services.Matlab import Matlab

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Variable global para almacenar la instancia de Muestras
madrid_muestra = None

@app.route('/parametrize_polygon', methods=['POST'])
def parametrize_polygon():
    global madrid_muestra
    try:
        print('Iniciando función parametrize_polygon')
        fecha_actual = datetime.datetime.now()
        fecha_hace_14_dias = fecha_actual - datetime.timedelta(days=80)

        # Recibir datos del polígono desde la solicitud POST
        data = request.get_json()
        print('Datos recibidos:', data)
        polygono = data['polygono']
        print('Datos recibidos:', polygono)
        print('Polígono:', polygono)
        
        # Crear la instancia de Muestras
        madrid_muestra = Muestras(
            utmX=None,
            utmY=None,
            polygono=polygono,
            timeZone=30,
            firstImage=fecha_hace_14_dias
        )
        print('madrid_muestra creada:', madrid_muestra)

        return jsonify({'message': 'Parámetros de polígono establecidos correctamente'})
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 500


@app.route('/get_sentinel', methods=['GET'])
def get_sentinel():
    global madrid_muestra
    try:
        if madrid_muestra is None:
            return jsonify({'error': 'madrid_muestra no está definida'}), 312

        # Obtener las muestras de satélite
        sentinel = ImagenesSentinel(madrid_muestra)
        print('ImagenesSentinel creado:', sentinel)
        sentinel.get_satelite_muestras()

        return jsonify( madrid_muestra.informaciones)
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 500


@app.route('/descargar', methods=['GET'])
def descargar():
    global madrid_muestra
    try:
        if madrid_muestra is None:
            return jsonify({'error': 'madrid_muestra no está definida'}), 312

        # Descargar imágenes de satélite
        sentinel = ImagenesSentinel(madrid_muestra)
        sentinel.descargar()
        
        return jsonify({'message': 'Imágenes descargadas correctamente'})
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 500


@app.route('/descomprimir', methods=['GET'])
def descomprimir():
    global madrid_muestra
    try:
        if madrid_muestra is None:
            return jsonify({'error': 'madrid_muestra no está definida'}), 312

        # Descomprimir imágenes de satélite
        sentinel = ImagenesSentinel(madrid_muestra)
        sentinel.descomprimir_zips()
        
        return jsonify({'message': 'Imágenes descomprimidas correctamente'})
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 500


@app.route('/acolite', methods=['GET'])
def acolite():
    global madrid_muestra
    try:
        if madrid_muestra is None:
            return jsonify({'error': 'madrid_muestra no está definida'}), 312

        # Procesar imágenes con Acolite
        a = Acolite(madrid_muestra)
        
        return jsonify({'message': 'Acolite procesado correctamente'})
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 500


@app.route('/simulacion', methods=['GET'])
def simulacion():
    global madrid_muestra
    try:
        if madrid_muestra is None:
            return jsonify({'error': 'madrid_muestra no está definida'}), 312

        parametros_completos = [
            {"raiz": "Nechad", "año": "2009", "banda": "ave", "ruta": "/path/to/tur_nechad2009ave"},
            {"raiz": "Nechad", "año": "2010", "banda": "ave", "ruta": "/path/to/spm_nechad2010"},
            {"raiz": "Nechad", "año": "2010", "banda": "", "ruta": "/path/to/spm_nechad2010ave"},
            {"raiz": "Nechad", "año": "2009", "banda": "", "ruta": "/path/to/tur_nechad2009"},
            {"raiz": "Nechad", "año": "2016", "banda": "", "ruta": "/path/to/tur_nechad2016"},
            {"raiz": "Dogliotti", "año": "2015", "banda": "", "ruta": "/path/to/tur_dogliotti2015"},
            {"raiz": "TUR_Novoa", "año": "2017", "banda": "", "ruta": "/path/to/tur_novoa2017"},
            {"raiz": "SPM_Novoa", "año": "2017", "banda": "", "ruta": "/path/to/spm_novoa2017"},
            {"raiz": "oc2", "año": "", "banda": "2", "ruta": "/path/to/chl_oc2"},
            {"raiz": "oc3", "año": "", "banda": "3", "ruta": "/path/to/chl_oc3"},
            {"raiz": "gons", "año": "", "banda": "740", "ruta": "/path/to/chl_re_gons"},
            {"raiz": "gons", "año": "", "banda": "", "ruta": "/path/to/chl_re_gons740"},
            {"raiz": "moses", "año": "", "banda": "3b740", "ruta": "/path/to/chl_re_moses3b"},
            {"raiz": "moses", "año": "", "banda": "3b", "ruta": "/path/to/chl_re_moses3b740"},
            {"raiz": "mishra", "año": "", "banda": "", "ruta": "/path/to/chl_re_mishra"},
            {"raiz": "ndci", "año": "", "banda": "", "ruta": "/path/to/ndci"},
            {"raiz": "ndvi", "año": "", "banda": "", "ruta": "/path/to/ndci"},
            {"raiz": "ndvi_rhot", "año": "", "banda": "", "ruta": "/path/to/ndci"},
            {"raiz": "chl_re", "año": "", "banda": "", "ruta": "/path/to/chl_re_bramich"},
            {"raiz": "rhos", "año": "", "banda": "", "ruta": "/path/to/chl_re_bramich"},
            {"raiz": "rgb", "año": "", "banda": "", "ruta": "/path/to/chl_re_bramich"},
            {"raiz": "rhow", "año": "", "banda": "", "ruta": "/path/to/chl_re_bramich"},
            {"raiz": "rhot", "año": "", "banda": "", "ruta": "/path/to/chl_re_bramich"}
        ] 
        
        b = Simulacion(madrid_muestra, parametros_completos)
        b.ejecutar_simulacion()

        return jsonify({'message': 'Simulación ejecutada correctamente', 'parametros': b.parametros})
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 500


@app.route('/matlab', methods=['GET'])
def matlab():
    global madrid_muestra
    try:
        output_dir = r"C:\\Users\\Luisbra\\Desktop\\funcional\\simulacion"
        matlab_instance = Matlab(output_dir)
        matlab_instance.crear_archivo_procesar_imagenes()
        matlab_instance.crear_archivo_transparencia()

        return jsonify({'message': 'Archivos Matlab creados correctamente'})
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, port=4300)

